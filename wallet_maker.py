# Make several wallets and back-up their private keys to a json

import os, json, string, random

from solders.keypair import Keypair


def make_cluster():
    file_name = f'cluster_{''.join(random.choice(string.ascii_uppercase) for _ in range(3))}.json'
    file_name = file_name
    wallet_list = []

    for _ in range(100):
        wallet = Keypair()

        public_key = str(wallet.pubkey())
        private_key = wallet.__str__()

        wallet_dict = {
            'public_key': public_key,
            'private_key': private_key,
        }

        wallet_list.append(wallet_dict)

    # Check if the file exists
    if not os.path.exists(file_name):
        # File doesn't exist, create it with initial data
        with open(file_name, 'w') as file:
            json.dump(wallet_list, file, indent=4)  # Start with new_data in a list

    else:
        # Read, update, and write
        with open(file_name, 'r+') as file:  # Open file in read/write mode
            # Load existing data
            data = json.load(file)
            # Append new data
            data.extend(wallet_list)
            # Reset file position to the beginning
            file.seek(0)
            # Write updated data
            json.dump(data, file, indent=4)
            # Truncate the file in case new data is smaller than the old
            file.truncate()

