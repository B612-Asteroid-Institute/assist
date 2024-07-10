#include <stdio.h>
#include <stdlib.h>
#include "spk.h"



void print_spk_data(struct spk_s *spk_data) {
    if (!spk_data) {
        printf("SPK data is NULL.\n");
        return;
    }

    // Print constants
    printf("Constants:\n");
    printf("EMRAT: %.16e\n", spk_data->con.EMRAT);
    printf("J2E: %.16e\n", spk_data->con.J2E);
    printf("J3E: %.16e\n", spk_data->con.J3E);
    printf("J4E: %.16e\n", spk_data->con.J4E);
    printf("J2SUN: %.16e\n", spk_data->con.J2SUN);
    printf("AU: %.16e\n", spk_data->con.AU);
    printf("RE: %.16e\n", spk_data->con.RE);
    printf("CLIGHT: %.16e\n", spk_data->con.CLIGHT);
    printf("ASUN: %.16e\n", spk_data->con.ASUN);

    // Print target data
    printf("\nTargets:\n");
    for (int i = 0; i < spk_data->num; i++) {
        struct spk_target *target = &spk_data->targets[i];
        printf("Target code: %d\n", target->code);
        printf("Center code: %d\n", target->cen);
        printf("Begin epoch: %.16e\n", target->beg);
        printf("End epoch: %.16e\n", target->end);
        printf("Mass: %.16e\n", target->mass);
        printf("Number of indices: %d\n", target->ind);
        printf("\n");
    }

    // Print mass data
    // printf("\nMass data:\n");
    // if (spk_data->masses.names == NULL || spk_data->masses.values == NULL) {
    //     printf("Mass data is NULL.\n");
    //     return;
    // }
    // for (int i = 0; i < spk_data->masses.count; i++) {
    //     printf("Name: %s\n", spk_data->masses.names[i]);
    //     printf("Value: %.16e\n", spk_data->masses.values[i]);
    //     printf("\n");
    // }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <path to .bsp file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *path = argv[1];
    struct spk_s *spk_data = assist_spk_init(path);
    if (!spk_data) {
        fprintf(stderr, "Failed to initialize SPK data.\n");
        return EXIT_FAILURE;
    }

    print_spk_data(spk_data);

    assist_spk_free(spk_data);

    return EXIT_SUCCESS;
}