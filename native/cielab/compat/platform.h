/* GPL-3.0-or-later. macOS removed the legacy finite() declaration.
 * Map that predicate to the equivalent C99 isfinite(), keeping the
 * vendored solver source unchanged. */
#ifndef ANACHROMA_PLATFORM_COMPAT_H
#define ANACHROMA_PLATFORM_COMPAT_H
#include <math.h>
static inline int anachroma_finite(double value) { return isfinite(value); }
#define finite anachroma_finite
#endif
