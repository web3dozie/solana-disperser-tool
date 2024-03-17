import glob, json, time

from solana.rpc.core import RPCException
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solders.keypair import Keypair
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price


def attempt_tx(client, wallet, tx):
    MAX_ATTEMPTS = 10  # Maximum number of retry attempts
    RETRY_DELAY = 1  # Delay between retries in seconds

    for attempt in range(MAX_ATTEMPTS):
        try:
            client.send_transaction(tx, wallet, recent_blockhash=client.get_latest_blockhash().value.blockhash)
            return

        except RPCException:
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
            else:
                print("\nMaximum attempts reached. Transaction failed.")


def send_funds_to_grifter():
    LAMPORT_PER_SOL = 1000000000

    def load_clusters():
        # List to store the lists of dicts from each file
        all_data = []

        # Use glob to find all files matching the specified pattern
        for filename in glob.glob('cluster_???.json'):
            # Make sure the part matches three uppercase letters
            if filename[8:11].isupper():
                try:
                    # Open and load the JSON file
                    with open(filename, 'r') as file:
                        data = json.load(file)
                        # Check if the data is a list (as expected)
                        if isinstance(data, list):
                            all_data.append(data)  # Extend the main list with this file's data
                        else:
                            print(f"Warning: The file {filename} does not contain a list.")
                except json.JSONDecodeError:
                    print(f"Error reading {filename}. Invalid JSON.")
                except Exception as e:
                    print(f"An error occurred with {filename}: {e}")

        return all_data

    clusters = load_clusters()

    grifter = Pubkey.from_string('71vBsieyUAbzyt3kaupPEVQ1GX3XB4PvuupNDZb3rFbE')

    sol_client = Client("https://lia-gf6xva-fast-mainnet.helius-rpc.com/")
    clust_count = 1
    for cluster in clusters:
        wallet_count = 0
        for wallet in cluster:
            sender = Keypair.from_base58_string(wallet['private_key'])

            transfer_ix = transfer(TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=grifter,
                lamports=int((0.00001 * LAMPORT_PER_SOL))))

            funding_tx = (Transaction()
                          .add(transfer_ix)
                          .add(set_compute_unit_limit(10_000_000))
                          .add(set_compute_unit_price(10_000)))

            attempt_tx(sol_client, sender, funding_tx)

            wallet_count += 1
            print(f'WALLET {wallet_count} ({wallet['public_key']}) DONE FOR CLUSTER {clust_count}')

        print(f'CLUSTER {clust_count} DONE')
        print('\n---------------------------------------------------\n')
        clust_count += 1

    print('ALL CLUSTERS DONE')
