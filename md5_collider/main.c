#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>

#include "md5.h"
#include "coll.h"



static void MDPrint (unsigned char digest[16]) {
  int i;

  for (i = 0; i < 16; i++)
    printf ("%02x", digest[i]);
}

static void MDFile (char *filename) {
  FILE *file;
  MD5_CTX context;
  int len, i;
  unsigned char buffer[1024], digest[16];

  if ((file = fopen (filename, "rb")) == NULL)
    printf ("%s can't be opened\n", filename);
  else {
    MD5Init (&context);
    while ( (len = fread (buffer, 1, 1024, file)) )
      MD5Update (&context, buffer, len);
    MD5Final (digest, &context);

    fclose (file);

    printf ("MD5 (%s) = ", filename);
    MDPrint( digest );
    printf ("\n");
  }
}

/*
int main (int argc, char **argv) {

  if (argc > 1)
    MDFile (argv[1]); // on calcule l'empreinte du fichier en argument...
  else {              // ...ou bien on fabrique une collision !
    MD5_CTX context;
    MD5Init( &context );
    uint32_t blockA0[16], blockA1[16], blockB0[16], blockB1[16];
    find_collision(context.state, blockA0, blockA1, blockB0, blockB1, 1);
  }

  return 0;
}
*/

int main (int argc, char **argv) {
  FILE *prefix_file, *output_file;
  MD5_CTX context;
  uint32_t msg1block0[16], msg1block1[16], msg2block0[16], msg2block1[16];
  int len, i;
  unsigned char buffer[1024], digest[16];

  if (argc != 4) {
    printf("usage : %s [prefix file] [output 1] [output 2]\n\n", argv[0]);
    printf("This generates two files, [output 1] and [output 2] such that :\n");
    printf("  #cat [prefix file] [output 1] | md5sum\n");
    printf("  #cat [prefix file] [output 2] | md5sum\n");
    printf("are equal. The size of [prefix file] must be a multiple of 64.\n\n");
    exit(0);
  }

  prefix_file = fopen(argv[1], "rb");
  if (prefix_file == NULL) {
    fprintf (stderr, "%s can't be opened\n", argv[1]);
    exit(1);
  }

  MD5Init (&context);
  while ( (len = fread (buffer, 1, 1024, prefix_file)) ) {
    MD5Update (&context, buffer, len);
    if ((len % 64) != 0) {
      fprintf (stderr, "The size of %s is not a multiple of 512 bits\n", argv[1]);
      exit(1);
    }
  }
  fclose(prefix_file);
  find_collision(context.state, msg1block0, msg1block1, msg2block0, msg2block1, 1);

  output_file = fopen(argv[2], "wb");
  if (output_file == NULL) {
    fprintf (stderr, "%s can't be opened\n", argv[2]);
    exit(1);
  }
  fwrite(msg1block0, 1, 64, output_file);
  fwrite(msg1block1, 1, 64, output_file);
  fclose(output_file);

  output_file = fopen(argv[3], "wb");
  if (output_file == NULL) {
    fprintf (stderr, "%s can't be opened\n", argv[3]);
    exit(1);
  }
  fwrite(msg2block0, 1, 64, output_file);
  fwrite(msg2block1, 1, 64, output_file);
  fclose(output_file);

  return 0;
}


