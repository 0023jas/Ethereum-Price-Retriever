from web3 import Web3
import json
import numpy as np

INFURA_API_KEY = ''
w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_API_KEY}'))

# Load Uniswap V3 Pool ABI
with open('abiContracts/uniswap_v3_pool_abi.json', 'r') as uniswap_v3_pool_json:
    uniswap_v3_pool_abi = json.load(uniswap_v3_pool_json)

# Load Uniswap V2 Pair ABI
with open('abiContracts/uniswap_v2_pool_abi.json', 'r') as uniswap_v2_pool_json:
    uniswap_v2_pool_abi = json.load(uniswap_v2_pool_json)

# Define Uniswap V3 pair contract addresses
V3_PAIR_ADDRESSES = {
    'ETH_USDC_1': '0x7BeA39867e4169DBe237d55C8242a8f2fcDcc387',
    'ETH_USDC_2': '0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
    'ETH_USDC_3': '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640',
    'ETH_USDC_4': '0xE0554a476A092703abdB3Ef35c80e0D76d32939F',
    'ETH_USDT_1': '0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36',
    'ETH_USDT_2': '0xC5aF84701f98Fa483eCe78aF83F11b6C38ACA71D',
    'ETH_USDT_3': '0x11b815efB8f581194ae79006d24E0d814B7697F6',
    'ETH_DAI_1': '0xC2e9F25Be6257c210d7Adf0D4Cd6E3E881ba25f8',
    'ETH_DAI_2': '0x60594a405d53811d3BC4766596EFD80fd545A270',
    'ETH_DAI_3': '0xa80964C5bBd1A0E95777094420555fead1A26c1e'
}

# Define Uniswap V2 pair contract addresses
V2_PAIR_ADDRESSES = {
    'ETH_USDC_1': '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc',
    'ETH_USDT_1': '0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852',
    'ETH_DAI_1': '0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11'
}

# Function to get reserves from Uniswap V3 and calculate Ethereum price
def v3_get_reserves(pair_name, block_number):
    pair_address = V3_PAIR_ADDRESSES[pair_name]
    pool_contract = w3.eth.contract(address=pair_address, abi=uniswap_v3_pool_abi)

    token0_address = pool_contract.functions.token0().call()
    token1_address = pool_contract.functions.token1().call()
    eth_address = w3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')

    usdc_address = w3.to_checksum_address('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
    dai_address = w3.to_checksum_address('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    usdt_address = w3.to_checksum_address('0xdAC17F958D2ee523a2206206994597C13D831ec7')

    slot0_data = pool_contract.functions.slot0().call(block_identifier=block_number)
    sqrt_price_x96 = slot0_data[0]

    # Calculate the price of token1 in terms of token0 using the square root price from the pool's slot0 data
    price_token1_token0 = (sqrt_price_x96 ** 2) / (1 << 192)

    if token0_address == eth_address:
        if token1_address == usdc_address:
            price_eth = price_token1_token0 * 1e12  # Multiply by 1e12 to account for USDC's 6 decimals
        elif token1_address == usdt_address:
            price_eth = price_token1_token0 * 1e12  # Multiply by 1e12 to account for USDT's 6 decimals
        elif token1_address == dai_address:
            price_eth = price_token1_token0   # Multiply by 1e18 to account for DAI's 18 decimals

    elif token1_address == eth_address:
        if token0_address == usdc_address:
            price_eth = (1 / price_token1_token0) * 1e12  # Multiply by 1e12 to account for USDC's 6 decimals
        elif token0_address == usdt_address:
            price_eth = (1 / price_token1_token0) * 1e12  # Multiply by 1e12 to account for USDT's 6 decimals
        elif token0_address == dai_address:
            price_eth = (1 / price_token1_token0)   # Multiply by 1e18 to account for DAI's 18 decimals

    else:
        price_eth = 0

    return price_eth

# Function to get reserves from Uniswap V2 and calculate Ethereum price
def v2_get_reserves(pair_name, block_number):
    pair_address = V2_PAIR_ADDRESSES[pair_name]
    pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v2_pool_abi)
    token0_address = pair_contract.functions.token0().call(block_identifier=block_number)
    token1_address = pair_contract.functions.token1().call(block_identifier=block_number)
    eth_address = w3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
    
    usdc_address = w3.to_checksum_address('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
    dai_address = w3.to_checksum_address('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    usdt_address = w3.to_checksum_address('0xdAC17F958D2ee523a2206206994597C13D831ec7')
    

    reserves = pair_contract.functions.getReserves().call(block_identifier=block_number)
    
    if token0_address == eth_address:
        if token1_address == usdc_address:
            reserve_eth = reserves[0] / 1e18  # ETH reserve
            reserve_stablecoin = reserves[1] / 1e6   # Stablecoin reserve
        elif token1_address == usdt_address:
            reserve_eth = reserves[0] / 1e18  # ETH reserve
            reserve_stablecoin = reserves[1] / 1e6   # Stablecoin reserve
        elif token1_address == dai_address:
            reserve_eth = reserves[0] / 1e18  # ETH reserve
            reserve_stablecoin = reserves[1] / 1e18   # Stablecoin reserve
            
    elif token1_address == eth_address:
        if token0_address == usdc_address:
            reserve_eth = reserves[1] / 1e18  # ETH reserve
            reserve_stablecoin = reserves[0] / 1e6   # Stablecoin reserve
        elif token0_address == usdt_address:
            reserve_eth = reserves[1] / 1e18  # ETH reserve
            reserve_stablecoin = reserves[0] / 1e6   # Stablecoin reserve
        elif token0_address == dai_address:
            reserve_eth = reserves[1] / 1e18  # ETH reserve
            reserve_stablecoin = reserves[0] / 1e18   # Stablecoin reserve
    
    ethereum_price = reserve_stablecoin / reserve_eth

    return ethereum_price

# Define the block number for which the Ethereum price should be calculated
block_number = 13000000

# Initialize a list to store the Ethereum prices
price_eth_list = []

# Iterate over Uniswap V3 pairs, calculate and store the Ethereum prices
for pair_name in V3_PAIR_ADDRESSES.keys():
    try:
        price_eth = v3_get_reserves(pair_name, block_number)
    except:
        price_eth = 0
    price_eth_list.append(price_eth)
    print(f"Price of Ethereum in {pair_name} at block {block_number}:")
    print(f"1 ETH = {price_eth:.4f} {pair_name.split('_')[1]}\n")

# Iterate over Uniswap V2 pairs, calculate and store the Ethereum prices
for pair_name in V2_PAIR_ADDRESSES.keys():
    try:
        price_eth = v2_get_reserves(pair_name, block_number)
    except:
        price_eth = 0
    price_eth_list.append(price_eth)
    print(f"Price of Ethereum in {pair_name} at block {block_number}:")
    print(f"1 ETH = {price_eth:.4f} {pair_name.split('_')[1]}\n")

# Remove zero prices from the list
price_eth_list = [x for x in price_eth_list if x != 0]

# Check if any prices are available
if(len(price_eth_list) == 0):
    print("No Data Available!")
    exit(1)
else:
    price_eth_list_unprocessed_avg = sum(price_eth_list) / len(price_eth_list)

# Calculate the median price
price_eth_list_median = np.median(price_eth_list)

# Calculate upper and lower bounds for filtering outliers
price_eth_list_upper_bound = price_eth_list_median + 0.2 * price_eth_list_median
price_eth_list_lower_bound = price_eth_list_median - 0.2 * price_eth_list_median

# Filter out the outliers
price_eth_list = [x for x in price_eth_list if (x >= price_eth_list_lower_bound) and (x <= price_eth_list_upper_bound)]

# Print the List of Ethereum Prices
print(price_eth_list)

# Calculate the average Ethereum price
price_eth_list_avg = sum(price_eth_list) / len(price_eth_list)

# Print the final Ethereum price
print("Ethereum Price in USD: " + str(price_eth_list_avg) + " at Block " + str(block_number))
        

