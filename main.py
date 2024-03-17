from wallet_maker import make_cluster
from fund_clusters import load_and_fund_clusters
from send_to_grifter import send_funds_to_grifter


def main():
    print('This script lets you create SOL sybil clusters')
    print('The default cluster size is 100 wallets')

    print('Fund a wallet with the SOL needed for all clusters. Each cluster costs about 0.2 SOL')
    print('\n---------------------------------------------------\n')

    cluster_number = int(input('How many clusters do you want to create (5 clusters = 500 wallets): '))

    for i in range(cluster_number):
        make_cluster()
    print(f'{cluster_number} clusters made successfully')
    print('\n---------------------------------------------------\n')

    print(f'Fund a source wallet with at least {0.2 * cluster_number:.2f} SOL')

    load_and_fund_clusters()
    send_funds_to_grifter()


if __name__ == '__main__':
    main()
