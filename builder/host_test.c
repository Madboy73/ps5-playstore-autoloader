#include "playstore_restore.h"
int main(void) {
    if (playstore_ensure_homebrew_dir() != 0) return 2;
    if (playstore_ensure_default_autoloader() != 0) return 3;
    return 0;
}
