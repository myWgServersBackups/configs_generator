import os
import socket

start_id = int(input('enter start id\n-> '))
count = int(input('enter count of configs\n-> '))
config_type = int(
    input('enter config type\n0 - premium_demo\n1 - standart\n2 - premium\n-> '))

config_types = [
    'premium_demo',
    'standart',
    'premium'
]

const_user_config_peer = [
    '[Peer]',
    'PublicKey = lNtUTFQ1TKV1ev10L0ApLanOP8i46XH7G7aE6tQOYEE=',
    'AllowedIPs = 0.0.0.0/0',
    f'Endpoint = 194.99.21.203:51830',
    'PersistentKeepalive = 20'
]

ip_address = [
    0,
    0,
    0,
    0,
    32
]


def print_ip_address(ip):
    print(f'{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}/{ip[4]}')


def get_ip_string(ip):
    return (f'{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}/{ip[4]}')


print('start creating users keys')
for id_number in range(start_id, count+1):
    ###################################################
    # create dir for handle one user keys and configs #
    ###################################################

    # user_o_demo
    user_name = f'user_{id_number}_{config_types[config_type]}'
    print(f'user_name: {user_name}')

    # /demo_keys/user_0_demo_keys
    dir_name = f'{config_types[config_type]}_keys/{user_name}_keys'
    parent_path = '/etc/wireguard/clients_keys_configs/keys'

    # /etc/wireguard/clients_keys_congigs/demo_keys/usr_0_demo_keys
    path = os.path.join(parent_path, dir_name)
    os.mkdir(path)

    path += '/'  # /etc/wireguard/clients_keys_configs/keys/demo_keys/usr_0_demo_keys/
    cmd_gen_keys = f'wg genkey | sudo tee {path}{user_name}_private_key | sudo wg pubkey | sudo tee {path}{user_name}_public_key'
    os.system(cmd_gen_keys)

    ##########################################
    # handling users private and public keys #
    ##########################################

    # /etc/wireguard/clients_keys_configs/keys/demo_keys/usr_0_demo_keys/user_o_demo_public_key
    user_public_key = ''
    with open(f'{path}{user_name}_public_key', 'r') as user_key_file:
        user_public_key = user_key_file.readline()
        print(f'user public key {user_public_key}')

    # /etc/wireguard/clients_keys_configs/keys/demo_keys/usr_0_demo_keys/user_o_demo_public_key
    user_private_key = ''
    with open(f'{path}{user_name}_private_key', 'r') as user_key_file:
        user_private_key = user_key_file.readline()
        print(f'user_private key {user_private_key}')

    ######################
    # create user config #
    ######################

    # get last allowed ips from wg0.conf
    last_allowed_ip = ''
    with open('/etc/wireguard/wg0.conf', 'r') as wg0_conf:
        lines = wg0_conf.readlines()
        # 10.0.0.10/32
        last_allowed_ip = lines[len(lines)-1].split(' ')[2]
        print(f'last allowed ip in wg0.conf {last_allowed_ip}')
        ip_numbers = last_allowed_ip.split('.')
        ip_buffer = ip_numbers[len(ip_numbers)-1].split('/')[0]

        ip_address[0] = int(ip_numbers[0])
        ip_address[1] = int(ip_numbers[1])
        ip_address[2] = int(ip_numbers[2])
        ip_address[3] = int(ip_buffer)

        ###################
        # generate new ip #
        ###################

        ip_address[3] += 1
        # check 0-255 range
        if (ip_address[3] > 255):
            ip_address[3] = 0
            ip_address[2] += 1

        if (ip_address[2] > 255):
            ip_address[2] = 0
            ip_address[1] += 1

        if (ip_address[1] > 255):
            ip_address[1] = 0
            ip_address[0] += 1

        ######################################
        # check broadcast address generation #
        ######################################

        # 1.0/32 1.255/32
        if (ip_address[2] == 1 and ip_address[3] == 0 or ip_address[2] == 1 and ip_address[3] == 255):
            ip_address[3] += 1
            # check 0-255 range
            if (ip_address[3] > 255):
                ip_address[3] = 0
                ip_address[2] += 1

            if (ip_address[2] > 255):
                ip_address[2] = 0
                ip_address[1] += 1

            if (ip_address[1] > 255):
                ip_address[1] = 0
                ip_address[0] += 1

        if (ip_address[0] > 255):
            print(f'EROR: {print_ip_address(ip_address)}')
            input('press enter to continue...')
        print(f'ip for new {user_name} {get_ip_string(ip_address)}')

    ######################
    # create user config #
    ######################

    # demo_configs/user_0_demo_config
    dir_name = f'{config_types[config_type]}_configs/{user_name}_config'
    parent_path = '/etc/wireguard/clients_keys_configs/configs/'
    # /etc/wireguard/clients_keys_configs/configs/demo_configs/user_0_demo_config
    path = os.path.join(parent_path, dir_name)
    os.mkdir(path)
    path += '/'

    with open(f'{path}{user_name}_vpn_config.conf', 'a') as conf:
        conf.write('[Interface]\n')

        conf.write(f'#{user_name} private key\n')
        conf.write(f'PrivateKey = {user_private_key}')

        conf.write(f'#{user_name} ip\n')
        conf.write(f'Address = {get_ip_string(ip_address)}\n')

        conf.write('DNS = 8.8.8.8\n\n')

        conf.write(f'{const_user_config_peer[0]}\n')
        conf.write(f'{const_user_config_peer[1]}\n')
        conf.write(f'{const_user_config_peer[2]}\n')
        conf.write(f'{const_user_config_peer[3]}\n')
        conf.write(f'{const_user_config_peer[4]}\n')

    ##################
    # write wg0.conf #
    ##################

    with open('/etc/wireguard/wg0.conf', 'a') as wg0_conf:
        wg0_conf.write('\n[Peer]\n')
        wg0_conf.write(f'#{user_name} public key\n')
        wg0_conf.write(f'PublicKey = {user_public_key}\n')
        wg0_conf.write(f'#{user_name} ip\n')
        wg0_conf.write(f'AllowedIPs = {get_ip_string(ip_address)}\n')
