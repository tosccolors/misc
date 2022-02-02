/*
    Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
    @author: Vincent Verheul (v.verheul@magnus.nl)
    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

    Converts a json file to a comma separated file compatible with Microsoft Excel.
    The json is expected to contain a list of lists as the value of the key "result".
    The first list (or row) is expected to contain the header with column names.
    Brackets within a text enclosed in single quotes (to separate them from list
    delimiters in the Visual Basic for Applications logic) will be stripped from
    their single quotes.
*/

// Compiler directives are used to compile on different platforms
// use gcc -dM -E - </dev/null on Mac or linux to show defined variables

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>

#ifdef _WIN64
const int os_ref = 1;
const char path_sep = '/';  // '\\';
#elif _WIN32
const int os_ref = 2;
const char path_sep = '/';  // '\\';
#elif __APPLE__
const int os_ref = 3;
const char path_sep = '/';
#elif __linux__
const int os_ref = 4;
const char path_sep = '/';
#else
const int os_ref = 9;
const char path_sep = '/';
#endif

struct options_type {                  // command line options
    bool use_utf8;                     // override default based on operating system
    bool use_semi;                     // use a semicolon instead of a comma separator
    bool use_tab;                      // use a tab instead of a comma separator
    bool unquoted;                     // use no quotes around strings
};
struct file_globals_type {             // file related variables
    char *path;                        // path derived from the input path & filename
    char *inp_filename;                // input filename
    char *out_filename;                // output filename
    char *stat_filename;               // statistics output filename
    char *path_and_name;               // combined path and filename
    char *buffer;                      // buffer to hold entire file plus 'extra_length' so output can be written from start
    char *inp_data;                    // input json data
    long extra_length;                 // additional file buffer length, should be the max expected record length
};
struct uni_globals_type {              // unicode global variables
    bool unicode_ini;                  // status of unicode data being initialised
    int unimax;                        // number of selected 'extended' ASCII characters
    char *unic_esc_code[112];          // unicode escape codes without the initial sequence \u
    char *unicode_seg[5];              // the first two digits of a unicode escape code are used as a 'segment'
};
struct uni_map_type {                  // per unicode escape code first two digits
    char *ansi_char;                   // mapped characters for this unicode escape code in ANSI (Windows)
    char utf8[255][4];                 // mapped multi-byte for this unicode escape code in UTF8 (Mac or by option on Windows)
    unsigned int ubound;               // upper bound for ansi_char array
};

struct uni_map_type unicode_map[5];    // mapping the unicode escape codes per segment to their ANSI and UTF8 characters
struct uni_globals_type uglob;         // global variables
struct file_globals_type fglob;        // file related global variables
struct options_type opt;               // option variables


void help_info()
// Print help information to the console
{
    printf("NAME\n");
    printf("\tOdooJsonToCsv\n\n");
    printf("DESCRIPTION\n");
    printf("\tThis utility program converts a JSON file to a CSV file. The JSON must contain a key \"result\".\n");
    printf("\tThe value for this key must be a single list which contains many lists (single nesting level).\n");
    printf("\tEach of these lists holds a number of values, with all lists the same # of values. The first \n");
    printf("\tlist usually holds the column names. It has the response JSON format from an Odoo application.\n\n");
    printf("OUTPUT\n");
    printf("\tThe output is a CSV file with the same name as the input file, but with extension csv.\n");
    printf("\tA second file with the name OdooJsonToCsv-Vars.txt is created which contains three variable values:\n");
    printf("\tFirst, a HTML style response code: 200 when OK, 400 when input not found, 500 for (server) errors.\n");
    printf("\tSecond, the number of rows (including the first header row) written to the CSV file.\n");
    printf("\tThird, the elapsed time in seconds. The values are on a single line separated by semicolons.\n\n");
    printf("REQUIRED ARGUMENT\n");
    printf("\tPass the path & filename (with extension) as the first parameter. Path is optional.\n\n");
    printf("OPTIONS\n");
    printf("\t--utf8\tOutput non-ascii characters in UTF-8, this is the default for non-Windows machines.\n");
    printf("\t--tab\tUse tab characters instead of commas to separate values.\n");
    printf("\t--semi\tUse semicolon characters instead of commas and replace decimal dot by decimal comma.\n");
    printf("\t--unquoted\tRemove double-quote characters around string values.\n");
}


void copy_n_string(char *Destination, char const *Source, rsize_t MaxCount)
// Copy source to destination string with indicated maximum characters, make sure Destination is Null terminated
{
    memcpy(Destination, Source, MaxCount);
    if (Destination[MaxCount] != '\0') { Destination[MaxCount] = '\0'; }
}


void concat_n_string(char *Destination, char const *Source, rsize_t ConcatLength)
// Concatenate source to destination string with indicated total length
// Compiler directive for Apple Mac library usage
{
#if __MACH__
    strlcat(Destination, Source, ConcatLength);
#else
    strcat_s(Destination, ConcatLength, Source);
#endif
}


unsigned int path_end(char *p_inp)
// Find end of path position in input string (return 0 when no path)
{
    unsigned int i = strlen(p_inp);
    while (i > 0 && p_inp[i] != '/' && p_inp[i] != '\\') { i -= 1; }
    return  i;
}


bool init_path_and_filename(int arg_count, char *arguments[])
// Set global path and inp_filename from command line arguments
{
    bool result = false;
    fglob.path = malloc(1024);
    fglob.inp_filename = malloc(1024);
    fglob.out_filename = malloc(1024);
    fglob.stat_filename = malloc(1024);
    fglob.path_and_name = malloc(2048);
    unsigned int i, p, offset, ext_len;
    if (arg_count > 0) {
        // set stat_filename
        p = path_end(arguments[0]);
        p += (p>0) ? 1: 0;
        i = p;
        ext_len = (strlen(arguments[0]) > 4 && arguments[0][((int) strlen(arguments[0]) - 4)] == '.') ? 4: 0;
        while (i < strlen(arguments[0]) - ext_len) { fglob.stat_filename[i-p] = arguments[0][i]; i += 1; }
        fglob.stat_filename[i-p] = '\0';
        i = strlen(fglob.stat_filename);
        if (fglob.stat_filename[i-3] == 'W' || fglob.stat_filename[i-3] == 'M') { fglob.stat_filename[i-3] = '\0'; }
        concat_n_string(fglob.stat_filename, "-Vars.txt", strlen(fglob.stat_filename)+11);
    }
    if (arg_count > 1) {
        if (strcmp(arguments[1], "-help") == 0 || strcmp(arguments[1], "--help") == 0) {
            help_info(); }
        else {
            // set path and filename
            fglob.path[0] = '\0';
            p = path_end(arguments[1]);
            if (p) { copy_n_string(fglob.path, arguments[1], p+1); }
            i = p;
            offset = (p>0) ? 1: 0;
            while (i < strlen(arguments[1])) {
                fglob.inp_filename[i - p] = arguments[1][i+offset];
                i += 1;
            }
            fglob.inp_filename[i - p] = '\0';
            i = strlen(fglob.inp_filename);
            while (i > 1 && fglob.inp_filename[i] != '.') { i -= 1; }
            if (fglob.inp_filename[i] != '.') { i = strlen(fglob.inp_filename); }
            copy_n_string(fglob.out_filename, fglob.inp_filename, i);
            concat_n_string(fglob.out_filename, ".csv", strlen(fglob.out_filename) + 5);
            result = true;
        }
    }
    else {
        help_info();
    }
    return result;
}


void command_line_options(int arg_count, char *arguments[])
// Handle additional command line options
{
    int i;
    opt.use_utf8 = (os_ref > 2);
    opt.use_semi = false;
    opt.use_tab = false;
    opt.unquoted = false;
    for (i=2; i < arg_count; i++) {
        if (strcmp(arguments[i], "-utf8") == 0 || strcmp(arguments[i], "--utf8") == 0)  opt.use_utf8 = true;
        if (strcmp(arguments[i], "-tab") == 0 || strcmp(arguments[i], "--tab") == 0)  opt.use_tab = true;
        if (strcmp(arguments[i], "-semi") == 0 || strcmp(arguments[i], "--semi") == 0)  opt.use_semi = true;
        if (strcmp(arguments[i], "-unquoted") == 0 || strcmp(arguments[i], "--unquoted") == 0)  opt.unquoted = true;
    }
    if (opt.use_tab && opt.use_semi) {opt.use_semi = false; }
    if (opt.use_utf8)  printf("Output in UTF-8\n");
    if (opt.use_tab)   printf("Output with Tab separators\n");
    if (opt.use_semi)  printf("Output with Semicolon separators\n");
    if (opt.unquoted)  printf("Output with unquoted strings\n");
    if (!opt.use_tab && !opt.use_semi && opt.unquoted) printf("Commas in strings will be replaced by spaces\n");
}


void set_path_file_name(bool is_output, bool is_stats_file)
// Combine path and filename for input and output files into variable path_and_name
{
    copy_n_string(fglob.path_and_name, fglob.path, strlen(fglob.path) + 1);
    if (is_stats_file) {
        concat_n_string(fglob.path_and_name, fglob.stat_filename, strlen(fglob.path) + strlen(fglob.stat_filename) + 2);
    }
    else if (is_output) {
        concat_n_string(fglob.path_and_name, fglob.out_filename, strlen(fglob.path) + strlen(fglob.out_filename) + 2);
    }
    else {
        concat_n_string(fglob.path_and_name, fglob.inp_filename, strlen(fglob.path) + strlen(fglob.inp_filename) + 1);
    }
}


bool create_stats_file(int status, long line_count, double elapsed)
// Write status 200 (OK) or 400 (not found) or 500 (error) with line count and elapsed time to statistics file
{
    FILE *statf = NULL;
    set_path_file_name(true, true);
#if __MACH__
    statf = fopen(fglob.path_and_name, "w");
#else
    fopen_s(&statf, fglob.path_and_name, "w");
#endif
    if (!statf) {
        printf("\nCould not open %s for output!\n", fglob.path_and_name);
        return false;
    }
    fprintf(statf,"%d;%ld;%f\n", status, line_count, elapsed);
    fclose(statf);
    return true;
}


bool remove_stats_file()
// Remove an existing statistics file
{
    int returnval;
    set_path_file_name(true, true);
    returnval = remove(fglob.path_and_name);
    return returnval;
}


long read_input_json_file()
// Read json text file into global string inp_data
{
    FILE *fp = NULL;
    long file_length = 0;
    set_path_file_name(false, false);
#if __MACH__
    fp = fopen(fglob.path_and_name, "rb");
#else
    fopen_s(&fp, fglob.path_and_name, "rb");
#endif
    if (fp) {
        fseek(fp, 0, SEEK_END);
        file_length = ftell(fp);
        fseek(fp, 0, SEEK_SET);
        fglob.buffer = malloc(file_length + fglob.extra_length);
        fglob.inp_data = (fglob.buffer + fglob.extra_length);
#if __MACH__
        fread(fglob.inp_data, file_length, 1, fp);
#else
        fread_s(fglob.inp_data, file_length, file_length, 1, fp);
#endif
        fclose(fp);
    }
    return file_length;
}


bool unicode_init()
// A selection of extended Ascii codes (between #128 and #255) that have a representation in both
// ANSI (Windows 1252) and UTF8 are mapped to their corresponding unicode escape codes.
{
    int i, j;
    unsigned int asc_code_ansi_vals[112] = {
            128, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 142, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 158, 159,
            161, 162, 163, 165, 167, 168, 169, 170, 171, 172, 174, 175, 176, 177, 180, 181, 182, 183, 184, 186, 187, 191, 192, 193, 194, 195, 196,
            197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 209, 210, 211, 212, 213, 214, 216, 217, 218, 219, 220, 221, 223, 224, 225, 226,
            227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 255,
            99, 105, 115, 32
    };
    unsigned char utf8_wide_char[112][3] = {
            {226, 130, 172}, {226, 128, 154}, {198, 146, 0}, {226, 128, 158}, {226, 128, 166}, {226, 128, 160}, {226, 128, 161}, {203, 134, 0}, {226, 128, 176}, {197, 160, 0},
            {226, 128, 185}, {197, 146, 0}, {197, 189, 0}, {226, 128, 152}, {226, 128, 153}, {226, 128, 156}, {226, 128, 157}, {198, 146, 0}, {226, 128, 147}, {226, 128, 148},
            {203, 156, 0}, {226, 132, 162}, {197, 161, 0}, {226, 128, 186}, {197, 147, 0}, {197, 190, 0}, {197, 184, 0}, {194, 161, 0}, {194, 162, 0}, {194, 163, 0},
            {194, 165, 0}, {194, 167, 0}, {194, 168, 0}, {194, 169, 0}, {194, 170, 0}, {194, 171, 0}, {194, 172, 0}, {194, 174, 0}, {194, 175, 0}, {194, 176, 0},
            {194, 177, 0}, {194, 180, 0}, {194, 181, 0}, {194, 182, 0}, {194, 183, 0}, {194, 184, 0}, {194, 186, 0}, {194, 187, 0}, {194, 191, 0}, {195, 128, 0},
            {195, 129, 0}, {195, 130, 0}, {195, 131, 0}, {195, 132, 0}, {195, 133, 0}, {195, 134, 0}, {195, 135, 0}, {195, 136, 0}, {195, 137, 0}, {195, 138, 0},
            {195, 139, 0}, {195, 140, 0}, {195, 141, 0}, {195, 142, 0}, {195, 143, 0}, {195, 145, 0}, {195, 146, 0}, {195, 147, 0}, {195, 148, 0}, {195, 149, 0},
            {195, 150, 0}, {195, 152, 0}, {195, 153, 0}, {195, 154, 0}, {195, 155, 0}, {195, 156, 0}, {195, 157, 0}, {195, 159, 0}, {195, 160, 0}, {195, 161, 0},
            {195, 162, 0}, {195, 163, 0}, {195, 164, 0}, {195, 165, 0}, {195, 166, 0}, {195, 167, 0}, {195, 168, 0}, {195, 169, 0}, {195, 170, 0}, {195, 171, 0},
            {195, 172, 0}, {195, 173, 0}, {195, 174, 0}, {195, 175, 0}, {195, 176, 0}, {195, 177, 0}, {195, 178, 0}, {195, 179, 0}, {195, 180, 0}, {195, 181, 0},
            {195, 182, 0}, {195, 183, 0}, {195, 184, 0}, {195, 185, 0}, {195, 186, 0}, {195, 187, 0}, {195, 188, 0}, {195, 191, 0},
            {99, 0, 0}, {105, 0, 0}, {115, 0, 0}, {32, 0, 0}
    };
    static char *unic_esc_code_vals[112] = {
            "20ac", "201a", "0192", "201e", "2026", "2020", "2021", "02c6", "2030", "0160", "2039", "0152", "017d", "2018", "2019", "201c", "201d", "2022", "2013", "2014", "02dc", "2122", "0161", "203a", "0153", "017e", "0178",
            "00a1", "00a2", "00a3", "00a5", "00a7", "00a8", "00a9", "00aa", "00ab", "00ac", "00ae", "00af", "00b0", "00b1", "00b4", "00b5", "00b6", "00b7", "00b8", "00ba", "00bb", "00bf", "00c0", "00c1", "00c2", "00c3", "00c4",
            "00c5", "00c6", "00c7", "00c8", "00c9", "00ca", "00cb", "00cc", "00cd", "00ce", "00cf", "00d1", "00d2", "00d3", "00d4", "00d5", "00d6", "00d8", "00d9", "00da", "00db", "00dc", "00dd", "00df", "00e0", "00e1", "00e2",
            "00e3", "00e4", "00e5", "00e6", "00e7", "00e8", "00e9", "00ea", "00eb", "00ec", "00ed", "00ee", "00ef", "00f0", "00f1", "00f2", "00f3", "00f4", "00f5", "00f6", "00f7", "00f8", "00f9", "00fa", "00fb", "00fc", "00ff",
            "010d", "0131", "015f", "00a0"};
    uglob.unicode_ini = false;
    uglob.unimax = 112;
    // assign values to global array
    for (i=0; i < uglob.unimax; i++) {
        uglob.unic_esc_code[i] = unic_esc_code_vals[i];
    }
    // segments for escape codes starting with 00, 01, 02, 20 and 21 (hex) respectively
    for (i=0; i < 5; i++) { uglob.unicode_seg[i] = malloc(3); }
    uglob.unicode_seg[0] = "00"; uglob.unicode_seg[1] = "01"; uglob.unicode_seg[2] = "02";
    uglob.unicode_seg[3] = "20"; uglob.unicode_seg[4] = "21";
    // determine upper bounds of mapping arrays per segment and initialize unicode_maps
    int seg_ix;
    char uni_seg[3] = {'0','0','\0'};
    char uni_hex[3] = {'0','0','\0'};
    unsigned int escval;
    unsigned int max;
    for (seg_ix=0; seg_ix < 5; seg_ix++) {
        max = 0;
        for(i=0; i < uglob.unimax; i++) {
            uni_seg[0] = uglob.unic_esc_code[i][0]; uni_seg[1] = uglob.unic_esc_code[i][1];
            uni_hex[0] = uglob.unic_esc_code[i][2]; uni_hex[1] = uglob.unic_esc_code[i][3];
            if (strcmp(uni_seg,uglob.unicode_seg[seg_ix]) == 0) {
                escval = strtoul(uni_hex, NULL, 16);
                if (escval > max) { max = escval; }
            }
        }
        unicode_map[seg_ix].ansi_char = malloc(max + 2);
        unicode_map[seg_ix].ansi_char[max + 1] = '\0';
        unicode_map[seg_ix].ubound = max;
    }
    // load mapping to ANSI and UTF8
    for (seg_ix=0; seg_ix < 5; seg_ix++) {
        for (i=0; i < unicode_map[seg_ix].ubound; i++) {
            unicode_map[seg_ix].ansi_char[i] = '?';  // default
        }
        for (i=0; i < uglob.unimax; i++) {
            uni_seg[0] = uglob.unic_esc_code[i][0]; uni_seg[1] = uglob.unic_esc_code[i][1];
            uni_hex[0] = uglob.unic_esc_code[i][2]; uni_hex[1] = uglob.unic_esc_code[i][3];
            if (strcmp(uni_seg, uglob.unicode_seg[seg_ix]) == 0) {
                escval = strtoul(uni_hex, NULL, 16);
                unicode_map[seg_ix].ansi_char[escval] = (char) asc_code_ansi_vals[i];
                for (j=0; j<3; j++) { unicode_map[seg_ix].utf8[escval][j] = (char) utf8_wide_char[i][j]; }
                unicode_map[seg_ix].utf8[escval][3] = '\0';
            }
        }
    }
    return true;
}


bool convert_unicode_esc(const char *uni_esc, char *converted)
// Convert 4 character unicode escape code to corresponding ANSI character or UTF8 multi-byte
{
    bool mapping_found = false;
    char uni_seg[3] = {'0','0','\0'};
    char uni_hex[3] = {'0','0','\0'};
    unsigned int escval;
    int seg_ix;
    if (!uglob.unicode_ini) { uglob.unicode_ini = unicode_init(); }
    uni_seg[0] = uni_esc[0]; uni_seg[1] = uni_esc[1];
    uni_hex[0] = uni_esc[2]; uni_hex[1] = uni_esc[3];
    int seg_num = strtol(uni_seg, NULL, 10);
    switch (seg_num) {
        case 0: seg_ix = 0; break;
        case 1: seg_ix = 1; break;
        case 2: seg_ix = 2; break;
        case 20: seg_ix = 3; break;
        case 21: seg_ix = 4; break;
        default: seg_ix = -1;
    }
    if (seg_ix > -1) {
        escval = strtoul(uni_hex, NULL, 16);
        if (escval <= unicode_map[seg_ix].ubound) {
            if (opt.use_utf8) {
//                for (i=0; i<2; i++) { converted[i] = unicode_map[seg_ix].utf8[escval][i]; }   Wrong
                converted[0] = unicode_map[seg_ix].utf8[escval][0];
                converted[1] = unicode_map[seg_ix].utf8[escval][1];
                converted[2] = unicode_map[seg_ix].utf8[escval][2];
                converted[3] = '\0';
            }
            else {
                converted[0] = unicode_map[seg_ix].ansi_char[escval];
                converted[1] = '\0';
            }
            mapping_found = true;
        }
    }
    return mapping_found;
}


long convert_line(char *p_inp, int line_len, char *p_outp)
// Convert escaped characters, unicode escape codes, remove spaces after comma field separators and remove null texts
// returns number of added output characters
{
    bool esc_char = false;
    bool qte_char = false;
    bool esc_quote = false;
    bool inside_str = false;
    bool converted = false;
    int i, skip_char;
    int line_char_seq = 0;
    char *start_p_outp = NULL;
    char *p_work = NULL;
    char conv_ch[5] = {'~','~','~','~','\0'};
    char uni_esc[5] = {'0','0','0','0','\0'};
    start_p_outp = p_outp;
    p_work = p_inp;
    while (line_char_seq < line_len) {
        line_char_seq += 1;
        qte_char = line_char_seq > 1 && *(p_work-1) == '\'' && line_char_seq + 2 <= line_len && *(p_work+1) == '\'';
        esc_char = line_char_seq > 1 && *(p_work-1) == '\\';
        esc_quote = (esc_char && *(p_work) == '"');
        converted = false;
        skip_char = 0;
        if (*p_work == '"' && !esc_quote) {
            inside_str = !inside_str;
            if (opt.unquoted) { skip_char = 1; }
        }
        if (inside_str) {
            // replace \" by (one or-) two double-quoute characters
            if (esc_quote) {
                conv_ch[0] = '"';
                if (opt.unquoted) {conv_ch[1] = '\0'; } else { conv_ch[1] = '"'; conv_ch[2] = '\0'; }
                p_outp -= 1; converted = true;
            }
            // replace \t (tab) by a space
            else if (esc_char && *(p_work) == 't') {
                conv_ch[0] = ' '; conv_ch[1] = '\0';
                p_outp -= 1; converted = true;
            }
            // replace '[' by [ also for closing bracket and angular brackets
            else if (qte_char && (*(p_work) == '[' || *(p_work) == ']' || *(p_work) == '{' || *(p_work) == '}') ) {
                conv_ch[0] = *p_work;
                conv_ch[1] = '\0';
                p_outp -= 1; p_work += 1; line_char_seq += 1; converted = true;
            }
            // convert unicode escape sequence
            else if (esc_char && *(p_work) == 'u' && line_char_seq < line_len-4) {
                uni_esc[0] = *(p_work+1); uni_esc[1] = *(p_work+2);
                uni_esc[2] = *(p_work+3); uni_esc[3] = *(p_work+4);
                convert_unicode_esc(uni_esc, conv_ch);
                p_outp -= 1; converted = true;
                skip_char += 5;
                line_char_seq += 4;
            }
            // replace comma by space when delimiter is comma and strings are unquoted
            else if (*(p_work) == ',' && !opt.use_tab && !opt.use_semi && opt.unquoted) {
                conv_ch[0] = ' '; conv_ch[1] = '\0';
                converted = true;
            }
        }
        else {
            // remove space after a comma field separator and optionally replace comma
            if (line_char_seq > 1 && *(p_work - 1) == ',' && *(p_work) == ' ') {
                skip_char = 1;
                // replace comma separator by a tab
                if (opt.use_tab) {
                    conv_ch[0] = '\t'; conv_ch[1] = '\0';
                    p_outp -= 1; converted = true;
                }
                // replace comma separator by a semicolon
                else if (opt.use_semi) {
                    conv_ch[0] = ';'; conv_ch[1] = '\0';
                    p_outp -= 1; converted = true;
                }
            }
            // replace decimal dot by decimal comma
            if (opt.use_semi && line_char_seq < line_len && *(p_work) == '.'
                && *(p_work+1) >= '0' && *(p_work+1) <= '9') {
                conv_ch[0] = ','; conv_ch[1] = '\0';
                converted = true;
            }
            // skip the word null
            if (line_char_seq <= line_len-4 && *(p_work+1) == 'n' && *(p_work+2) == 'u' &&
                *(p_work+3) == 'l' && *(p_work+4) == 'l') {
                skip_char = 5;
                line_char_seq += 4;
            }
        }

        if (converted) {
            for (i=0; i<strlen(conv_ch); i++) { *p_outp = conv_ch[i]; p_outp +=1; }
        }
        else if (!skip_char) {
            *p_outp = *p_work; p_outp += 1;
        }
        p_work += skip_char ? skip_char: 1;
    }
    *p_outp = '\n'; p_outp += 1;
    return p_outp - start_p_outp;
}


long convert_json_to_csv(long file_size)
// Convert Odoo response json having a list of lists to a CSV file
{
    long lcount = 0;
    bool is_delim;
    int line_len;
    char *p_head = NULL;
    char *p_tail = NULL;
    char *p_work = NULL;
    char *p_outp = NULL;
    long out_line_len;
    long ouf_file_len = 0;
    long in_file_pos = 0;
    clock_t timer;
    timer = clock();
    remove_stats_file();
    FILE *outf = NULL;
    set_path_file_name(true, false);
#if __MACH__
    outf = fopen(fglob.path_and_name, "w");
#else
    fopen_s(&outf, fglob.path_and_name, "w");
#endif
    if (!outf) {
        printf("\nCould not open %s for output!\n", fglob.path_and_name);
        create_stats_file(400, 0, 0);
        exit(1);
    }
    p_outp = fglob.buffer;
    p_work = fglob.inp_data;
    p_head = strchr(p_work, '[');
    p_head +=1;
    p_tail = p_head;
//    char input_line[5000];
    while (in_file_pos < file_size && p_tail != NULL) {
        // find start of line
        is_delim = false;
        while (!is_delim) {
            p_work = strchr(p_tail, '[');
            if (p_work == NULL) { break; }
            p_head = p_work + 1;
            is_delim = (!(*(p_work-1) == '\'' && *(p_work+1) == '\''));
        }
        if (p_work == NULL) { break; }
        // find end of the line
        is_delim = false;
        while (!is_delim) {
            p_work += 1;
            p_work = strchr(p_work, ']');
            if (p_work == NULL) { break; }
            p_tail = p_work;
            is_delim = (!(*(p_work-1) == '\'' && *(p_work+1) == '\''));
        }
        lcount += 1;
        line_len = p_tail - p_head;
//        copy_n_string(input_line, p_head, line_len);
//        printf("%s\n", input_line);
        out_line_len = convert_line(p_head, line_len, p_outp);
        p_outp += out_line_len;
        ouf_file_len += out_line_len;
        if (p_outp >= p_head) {
            printf("\nBuffer size exceeded, lines too long?\n");
            create_stats_file(500, 0, 0);
            exit(1);
        }
        if (lcount % 10000 == 0) {printf("%ld lines\r", lcount);}
        in_file_pos = (p_work - fglob.inp_data);
    }
    *p_outp = '\0';
    if (lcount > 10000) {printf("saving %ld lines\r", lcount);}
    fprintf(outf,"%s", fglob.buffer);
    fclose(outf);
    timer = clock() - timer;
    create_stats_file(200, lcount, ((double)timer)/CLOCKS_PER_SEC);
    return lcount;
}


bool proper_json(long file_size)
// Check for the "result" key and a value starting with [[ (list of lists)
{
    char * p_work = NULL;
    int char_count = 0;
    bool is_proper = false;
    if (file_size == 0) { return false; }
    p_work = fglob.inp_data;
    p_work = strchr(p_work, '"');
    if (p_work != NULL) {
        while (!is_proper && char_count < 1000 && char_count < file_size - 20) {
            if (*(p_work+0) == 'r' && *(p_work+1) == 'e' && *(p_work+2) == 's' && *(p_work+3) == 'u' &&
                *(p_work+4) == 'l' && *(p_work+5) == 't' && *(p_work+6) == '"' && *(p_work+7) == ':' &&
                *(p_work+8) == ' ' && *(p_work+9) == '[' && *(p_work+10) == '[')
            { is_proper = true; }
            else {
                p_work += 1;
                p_work = strchr(p_work, '"');
                p_work += 1;
                char_count = p_work - fglob.inp_data;
            }
        }
    }
    return is_proper;
}


int main(int arg_count, char *arguments[]) {
    if (init_path_and_filename(arg_count, arguments)) {
        printf("Path: %s\nInput-filename: %s\n", fglob.path, fglob.inp_filename);
    }
    else {exit(1);}
    command_line_options(arg_count, arguments);
    fglob.extra_length = 10 * 1024;
    long file_size = read_input_json_file();
    if (file_size==0) {
        printf("\nEmpty or non existing file\n");
        create_stats_file(400, 0, 0);
        return 1;
    }
    if (!proper_json(file_size)) {
        printf("\nNot a proper JSON file\n");
        create_stats_file(401, 0, 0);
        return 1;
    }
    printf("\nRead %ld bytes\n", file_size);
    if (file_size > 0) {
        long line_count = convert_json_to_csv(file_size);
        printf("Output %ld lines\n", line_count);
        free(fglob.buffer);
        return 0;
    }
}
