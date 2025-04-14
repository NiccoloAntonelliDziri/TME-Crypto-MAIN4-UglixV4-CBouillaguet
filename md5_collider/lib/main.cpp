#include <iostream>
#include <fstream>
#include <time.h>

#include "main.hpp"

using namespace std;

void real_find_collision(const uint32 IV[], uint32 msg1block0[], uint32 msg1block1[], uint32 msg2block0[], uint32 msg2block1[], int verbose)
{
	seed32_1 = uint32(time(NULL));
	seed32_2 = 0x12345678;

	if (verbose)
		cout << "Generating first block: " << flush;
	find_block0(msg1block0, IV);

	uint32 IHV[4] = { IV[0], IV[1], IV[2], IV[3] };
	md5_compress(IHV, msg1block0);

	if (verbose)
		cout << endl << "Generating second block: " << flush;
	find_block1(msg1block1, IHV);

	for (int t = 0; t < 16; ++t)
	{
		msg2block0[t] = msg1block0[t];
		msg2block1[t] = msg1block1[t];
	}
	msg2block0[4] += 1 << 31; msg2block0[11] += 1 << 15; msg2block0[14] += 1 << 31;
	msg2block1[4] += 1 << 31; msg2block1[11] -= 1 << 15; msg2block1[14] += 1 << 31;
	if (verbose)
		cout << endl;
}


 extern "C" void find_collision(const uint32 IV[], uint32 msg1block0[], uint32 msg1block1[], uint32 msg2block0[], uint32 msg2block1[], int verbose) {
  real_find_collision(IV, msg1block0, msg1block1, msg2block0, msg2block1, verbose);
}

