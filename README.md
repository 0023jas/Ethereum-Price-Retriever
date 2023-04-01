# Ethereum Price Retriever

Ethereum Price Retriever is a Python app that fetches historical Ethereum prices from Uniswap V2 and V3 exchanges. It calculates the average ETH price at a specified block number using reserve data for USD stablecoin pairs (USDC, USDT, DAI), filtering outliers. Ideal for data analysis, trading, and research in cryptocurrencies.

## Prerequisites

- Python 3.6 or higher
- Install required libraries:

```bash
pip install web3 numpy
```

## Files required

- `abiContracts/uniswap_v3_pool_abi.json`: JSON file containing the Uniswap V3 Pool ABI
- `abiContracts/uniswap_v2_pool_abi.json`: JSON file containing the Uniswap V2 Pair ABI

## Usage

1. Set the `INFURA_API_KEY` variable to your own Infura API key.
2. Set the `block_number` variable to the desired Ethereum block number for which you want to calculate the Ethereum price.
3. Run the script using Python:

```bash
python eth_price_retrieval.py
```

## Output

The script will output the calculated Ethereum price for each Uniswap V2 and V3 pair. It will then calculate the average Ethereum Price by removing all 0 values returned and then removing all outliers.
