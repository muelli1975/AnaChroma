/* PNG-only CLI for the unchanged upstream CIELab method.
 * Copyright (c) 2026 Christoph Müller. GPL-3.0-or-later.
 * Input/output is RGB8, matching the separate PNG halves in AnaChroma/Batch. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <png.h>
#include "cv.h"
#ifdef _WIN32
#include <windows.h>
#include <wchar.h>
#endif

void method_init(void);
void method_free(void);
CvScalar method_combine_pixels(CvScalar left, CvScalar right);

static FILE *open_path(const char *path, const char *mode) {
#ifdef _WIN32
    int length = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, path, -1, NULL, 0);
    if (!length) return NULL;
    wchar_t *wide = malloc((size_t)length * sizeof(wchar_t));
    if (!wide) return NULL;
    MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, path, -1, wide, length);
    FILE *file = _wfopen(wide, strcmp(mode, "rb") == 0 ? L"rb" : L"wb");
    free(wide);
    return file;
#else
    return fopen(path, mode);
#endif
}

static unsigned char *read_png(const char *path, png_image *image) {
    memset(image, 0, sizeof(*image));
    image->version = PNG_IMAGE_VERSION;
    FILE *file = open_path(path, "rb");
    if (!file) { fprintf(stderr, "Cannot open input: %s\n", path); return NULL; }
    unsigned char *data = NULL;
    if (!png_image_begin_read_from_stdio(image, file)) goto done;
    /* Enforce the pipeline's RGB8 contract, avoid implicit gamma/alpha handling. */
    if (image->format != PNG_FORMAT_RGB || image->width == 0 || image->height == 0 ||
        (uint64_t)image->width * image->height > SIZE_MAX / 3) {
        fprintf(stderr, "Expected nonempty RGB8 PNG: %s\n", path);
        goto done;
    }
    data = malloc(PNG_IMAGE_SIZE(*image));
    if (!data) { fprintf(stderr, "Out of memory\n"); goto done; }
    if (!png_image_finish_read(image, NULL, data, 0, NULL)) { free(data); data = NULL; }
done:
    if (!data && image->message[0]) fprintf(stderr, "PNG input error: %s\n", image->message);
    png_image_free(image);
    fclose(file);
    return data;
}

static unsigned char byte_value(double value) {
    /* OpenCV cvSet2D rounded to nearest integer, then saturated to RGB8.
     * nearbyint preserves the normal ties-to-even rounding mode. */
    if (!isfinite(value) || value < 0) return 0;
    if (value > 255) return 255;
    return (unsigned char)nearbyint(value);
}

static int run(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        puts("CIELab PNG port 1.0; anaglyph 4db4253; GPL-3.0-or-later"); return 0;
    }
    if (argc != 5 || (strcmp(argv[3], "-o") && strcmp(argv[3], "--output"))) {
        fprintf(stderr, "Usage: cielab left.png right.png -o output.png\nRGB8 PNG halves of equal size; no video or display mode.\n");
        return argc == 2 && strcmp(argv[1], "--help") == 0 ? 0 : 2;
    }
    png_image left_info, right_info;
    unsigned char *left = read_png(argv[1], &left_info);
    if (!left) return 1;
    unsigned char *right = read_png(argv[2], &right_info);
    if (!right) { free(left); return 1; }
    if (left_info.width != right_info.width || left_info.height != right_info.height) {
        fprintf(stderr, "Left/right dimensions differ\n"); free(left); free(right); return 1;
    }
    size_t pixels = (size_t)left_info.width * left_info.height;
    unsigned char *output = malloc(pixels * 3);
    if (!output) { fprintf(stderr, "Out of memory\n"); free(left); free(right); return 1; }
    method_init();
    for (size_t index = 0; index < pixels * 3; index += 3) {
        CvScalar result = method_combine_pixels(
            cvScalar(left[index+2], left[index+1], left[index], 0),
            cvScalar(right[index+2], right[index+1], right[index], 0));
        output[index] = byte_value(result.val[2]);
        output[index+1] = byte_value(result.val[1]);
        output[index+2] = byte_value(result.val[0]);
    }
    method_free();
    free(left); free(right);
    png_image out_info;
    memset(&out_info, 0, sizeof(out_info));
    out_info.version = PNG_IMAGE_VERSION;
    out_info.width = left_info.width; out_info.height = left_info.height;
    out_info.format = PNG_FORMAT_RGB;
    FILE *file = open_path(argv[4], "wb");
    int success = file && png_image_write_to_stdio(&out_info, file, 0, output, 0, NULL);
    if (!success) fprintf(stderr, "Cannot write output PNG: %s\n", out_info.message);
    if (file && fclose(file) != 0) success = 0;
    png_image_free(&out_info); free(output);
    return success ? 0 : 1;
}

#ifdef _WIN32
int wmain(int argc, wchar_t **wide) {
    char **args = calloc((size_t)argc, sizeof(char *));
    if (!args) return 1;
    for (int i = 0; i < argc; ++i) {
        int size = WideCharToMultiByte(CP_UTF8, 0, wide[i], -1, NULL, 0, NULL, NULL);
        args[i] = malloc((size_t)size);
        if (!args[i]) { for (int j = 0; j < i; ++j) free(args[j]); free(args); return 1; }
        WideCharToMultiByte(CP_UTF8, 0, wide[i], -1, args[i], size, NULL, NULL);
    }
    int result = run(argc, args);
    for (int i = 0; i < argc; ++i) free(args[i]);
    free(args); return result;
}
#else
int main(int argc, char **argv) { return run(argc, argv); }
#endif
