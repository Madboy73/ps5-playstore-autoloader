#include "playstore_restore.h"
#include "playstore_default_pack.h"
#include "inflate.h"

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define PLAYSTORE_AUTOLOAD_DIR "/data/ps5_autoloader"
#define PLAYSTORE_AUTOLOAD_CONFIG "/data/ps5_autoloader/autoload.txt"
#define PLAYSTORE_HOMEBREW_DIR "/data/homebrew"

static int ensure_dir(const char *path) {
    struct stat st;
    if (stat(path, &st) == 0)
        return S_ISDIR(st.st_mode) ? 0 : -1;
    if (mkdir(path, 0777) == 0)
        return 0;
    if (errno == EEXIST && stat(path, &st) == 0 && S_ISDIR(st.st_mode))
        return 0;
    return -1;
}

int playstore_ensure_homebrew_dir(void) {
    int rc = ensure_dir(PLAYSTORE_HOMEBREW_DIR);
    if (rc == 0)
        printf("[playstore] homebrew directory ready: %s\n", PLAYSTORE_HOMEBREW_DIR);
    else
        printf("[playstore] WARNING: could not create %s (errno=%d)\n", PLAYSTORE_HOMEBREW_DIR, errno);
    fflush(stdout);
    return rc;
}

static uint32_t crc32_bytes(const unsigned char *data, size_t size) {
    uint32_t crc = 0xffffffffu;
    for (size_t i = 0; i < size; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j)
            crc = (crc >> 1) ^ (0xedb88320u & (uint32_t)-(int32_t)(crc & 1u));
    }
    return ~crc;
}

static int verify_file_exact(const char *path, const unsigned char *expected, size_t expected_size) {
    struct stat st;
    if (stat(path, &st) != 0 || (size_t)st.st_size != expected_size)
        return -1;
    FILE *f = fopen(path, "rb");
    if (!f) return -1;
    unsigned char buf[16384];
    size_t pos = 0;
    while (pos < expected_size) {
        size_t want = expected_size - pos;
        if (want > sizeof(buf)) want = sizeof(buf);
        size_t got = fread(buf, 1, want, f);
        if (got != want || memcmp(buf, expected + pos, want) != 0) {
            fclose(f);
            return -1;
        }
        pos += got;
    }
    int extra = fgetc(f);
    fclose(f);
    return extra == EOF ? 0 : -1;
}

static int write_file_atomic(const char *name, const unsigned char *data, size_t size) {
    char final_path[1024], temp_path[1024];
    if (!name || !name[0] || strchr(name, '/') || strstr(name, ".."))
        return -1;
    int n1 = snprintf(final_path, sizeof(final_path), "%s/%s", PLAYSTORE_AUTOLOAD_DIR, name);
    int n2 = snprintf(temp_path, sizeof(temp_path), "%s/.%s.playstore.tmp", PLAYSTORE_AUTOLOAD_DIR, name);
    if (n1 <= 0 || n2 <= 0 || (size_t)n1 >= sizeof(final_path) || (size_t)n2 >= sizeof(temp_path))
        return -1;
    FILE *f = fopen(temp_path, "wb");
    if (!f) return -1;
    size_t pos = 0;
    while (pos < size) {
        size_t chunk = size - pos;
        if (chunk > 65536) chunk = 65536;
        if (fwrite(data + pos, 1, chunk, f) != chunk) {
            fclose(f); unlink(temp_path); return -1;
        }
        pos += chunk;
    }
    if (fflush(f) != 0) { fclose(f); unlink(temp_path); return -1; }
    int fd = fileno(f);
    if (fd >= 0) (void)fsync(fd);
    if (fclose(f) != 0) { unlink(temp_path); return -1; }
    if (verify_file_exact(temp_path, data, size) != 0) { unlink(temp_path); return -1; }
    if (rename(temp_path, final_path) != 0) { unlink(temp_path); return -1; }
    return verify_file_exact(final_path, data, size);
}

static int restore_entry(const playstore_pack_entry_t *e) {
    unsigned char *raw = (unsigned char *)malloc(e->original_size ? e->original_size : 1);
    if (!raw) return -1;
    unsigned long out_len = (unsigned long)e->original_size;
    unsigned long in_len = (unsigned long)e->compressed_size;
    int rc = puff(raw, &out_len, e->compressed_data, &in_len);
    if (rc != 0 || out_len != e->original_size || crc32_bytes(raw, e->original_size) != e->crc32) {
        free(raw);
        return -1;
    }
    rc = write_file_atomic(e->name, raw, e->original_size);
    free(raw);
    return rc;
}

int playstore_ensure_default_autoloader(void) {
    struct stat st;
    if (stat(PLAYSTORE_AUTOLOAD_CONFIG, &st) == 0 && S_ISREG(st.st_mode)) {
        printf("[playstore] existing autoload config preserved: %s\n", PLAYSTORE_AUTOLOAD_CONFIG);
        fflush(stdout);
        return 0;
    }

    if (ensure_dir(PLAYSTORE_AUTOLOAD_DIR) != 0) {
        printf("[playstore] ERROR: could not create %s (errno=%d)\n", PLAYSTORE_AUTOLOAD_DIR, errno);
        fflush(stdout);
        return -1;
    }

    printf("[playstore] /data autoload missing; restoring default package...\n");
    fflush(stdout);

    /* Generator guarantees autoload.txt is last. It is the commit marker. */
    for (size_t i = 0; i < g_playstore_default_pack_count; ++i) {
        const playstore_pack_entry_t *e = &g_playstore_default_pack[i];
        printf("[playstore] restore: %s%s\n", e->name, e->is_config ? " [config-last]" : "");
        fflush(stdout);
        if (restore_entry(e) != 0) {
            printf("[playstore] ERROR: restore failed for %s\n", e->name);
            fflush(stdout);
            return -1;
        }
    }

    if (stat(PLAYSTORE_AUTOLOAD_CONFIG, &st) != 0 || !S_ISREG(st.st_mode)) {
        printf("[playstore] ERROR: restored config is missing\n");
        fflush(stdout);
        return -1;
    }

    printf("[playstore] default package restore complete\n");
    fflush(stdout);
    return 0;
}
