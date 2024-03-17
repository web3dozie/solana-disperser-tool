import glob, json, time

from concurrent.futures import ThreadPoolExecutor, wait
from solana.rpc.api import Client
from solana.rpc.core import RPCException
from solana.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer


def attempt_tx(client, wallet, tx):
    MAX_ATTEMPTS = 10  # Maximum number of retry attempts
    RETRY_DELAY = 1  # Delay between retries in seconds

    for attempt in range(MAX_ATTEMPTS):
        try:
            client.send_transaction(tx, wallet, recent_blockhash=client.get_latest_blockhash().value.blockhash)
            return 1

        except RPCException:
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
            else:
                print("Maximum attempts reached. Transaction failed.")
                return 0


def load_and_fund_clusters():
    LAMPORT_PER_SOL = 1000000000

    overlord_wallet = Keypair.from_base58_string(input('Enter the private key for the'
                                                       ' source wallet (Phantom Style): '))
    sol_client = Client("https://mainnet.helius-rpc.com/?api-key=73a9ec0a-9bb8-4c04-a886-d26b7824e3d3")

    # Make a list of clusters based on the JSON files
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

    # Fund the first wallet in each cluster with a certain amount of SOL
    funding_amt = 0.0015
    seeding_amt = funding_amt * (len(clusters[0]) + 1)

    print(f'There are {len(clusters)} CLUSTERS\n')

    count_ = 0
    '''
    for cluster in clusters:
        first_wallet = Pubkey.from_string(cluster[0]["public_key"])

        transfer_ix = transfer(TransferParams(
            from_pubkey=overlord_wallet.pubkey(),
            to_pubkey=first_wallet,
            lamports=int((seeding_amt * LAMPORT_PER_SOL))))

        funding_tx = (Transaction()
                      .add(transfer_ix)
                      .add(set_compute_unit_limit(10_000_000))
                      .add(set_compute_unit_price(10_000)))

        attempt_tx(sol_client, overlord_wallet, funding_tx)

        count_ += 1
        print(f'CLUSTER {count_} HAS BEEN SEEDED')
    

    print('\nALL CLUSTERS SEEDED')
    time.sleep(15)
    print('\n---------------------------------------------------\n')
    '''

    # fund the rest of the wallets in the cluster from the first wallet in the cluster

    def fund_wallets(cluster):
        _count = 1
        mini_overlord = Keypair.from_base58_string(cluster[0]["private_key"])
        wallet_count = 0
        # Fund individual wallets within the cluster
        for wallet in cluster[1:]:

            transfer_ix = transfer(TransferParams(
                from_pubkey=mini_overlord.pubkey(),
                to_pubkey=Pubkey.from_string(wallet["public_key"]),
                lamports=int((funding_amt * LAMPORT_PER_SOL))))

            funding_tx = (Transaction()
                          .add(transfer_ix)
                          .add(set_compute_unit_limit(10_000_000))
                          .add(set_compute_unit_price(10_000)))

            outcome = attempt_tx(sol_client, mini_overlord, funding_tx)
            if not outcome:
                print(f'Failed to fund: {wallet["public_key"]} from Cluster {_count}')
            else:
                print(f'Wallet {wallet_count} in Cluster {_count} has been funded')

        print(f'WALLETS IN CLUSTER {_count} FULLY FUNDED')
        _count += 1

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fund_wallets, cluster) for cluster in clusters]

        # This will block until all futures are done
        done, not_done = wait(futures)

    print('ALL CLUSTERS FUNDED')
    print('\n---------------------------------------------------\n')
