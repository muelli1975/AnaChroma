/* GPL-3.0-or-later. Only the scalar value container used by unchanged upstream
 * CIELab math. No OpenCV image implementation or algorithm is reproduced. */
#ifndef ANACHROMA_SCALAR_COMPAT_H
#define ANACHROMA_SCALAR_COMPAT_H
#include <stdlib.h>
typedef struct { double val[4]; } CvScalar;
static inline CvScalar cvScalar(double a, double b, double c, double d) {
    CvScalar value = {{a, b, c, d}};
    return value;
}
#endif
