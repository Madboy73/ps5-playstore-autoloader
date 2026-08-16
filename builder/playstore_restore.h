#pragma once

/* Create /data/homebrew only when absent. Existing contents are never touched. */
int playstore_ensure_homebrew_dir(void);

/* If /data/ps5_autoloader/autoload.txt is absent, restore the embedded
 * Playstore default package. Returns 0 if already present or restored, -1
 * on restore failure. Existing unrelated files are never deleted.
 */
int playstore_ensure_default_autoloader(void);
