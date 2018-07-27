import sys
import json
import web3
import time

from web3 import Web3, HTTPProvider, TestRPCProvider
from solc import compile_source
from web3.contract import ConciseContract

w3 = Web3(HTTPProvider("http://localhost:8545"))

market_address = sys.argv[1]

print("Market Address: " + market_address)

with open("market/contracts/build/contracts/Market.json", "r") as abi_definition:
    info_json = json.load(abi_definition)
    abi = info_json["abi"]

market_contract = w3.eth.contract(address=market_address, abi=abi)

# Create two ERC20 contracts
ERC20 = '''
pragma solidity ^0.4.16;

interface tokenRecipient { function receiveApproval(address _from, uint256 _value, address _token, bytes _extraData) external; }

contract TokenERC20 {
    // Public variables of the token
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    // 18 decimals is the strongly suggested default, avoid changing it
    uint256 public totalSupply;

    // This creates an array with all balances
    mapping (address => uint256) public balanceOf;
    mapping (address => mapping (address => uint256)) public allowance;

    // This generates a public event on the blockchain that will notify clients
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    // This generates a public event on the blockchain that will notify clients
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

    // This notifies clients about the amount burnt
    event Burn(address indexed from, uint256 value);

    /**
     * Constructor function
     *
     * Initializes contract with initial supply tokens to the creator of the contract
     */
    function TokenERC20(
        uint256 initialSupply,
        string tokenName,
        string tokenSymbol
    ) public {
        totalSupply = initialSupply * 10 ** uint256(decimals);  // Update total supply with the decimal amount
        balanceOf[msg.sender] = totalSupply;                // Give the creator all initial tokens
        name = tokenName;                                   // Set the name for display purposes
        symbol = tokenSymbol;                               // Set the symbol for display purposes
    }

    /**
     * Internal transfer, only can be called by this contract
     */
    function _transfer(address _from, address _to, uint _value) internal {
        // Prevent transfer to 0x0 address. Use burn() instead
        require(_to != 0x0);
        // Check if the sender has enough
        require(balanceOf[_from] >= _value);
        // Check for overflows
        require(balanceOf[_to] + _value >= balanceOf[_to]);
        // Save this for an assertion in the future
        uint previousBalances = balanceOf[_from] + balanceOf[_to];
        // Subtract from the sender
        balanceOf[_from] -= _value;
        // Add the same to the recipient
        balanceOf[_to] += _value;
        emit Transfer(_from, _to, _value);
        // Asserts are used to use static analysis to find bugs in your code. They should never fail
        assert(balanceOf[_from] + balanceOf[_to] == previousBalances);
    }

    /**
     * Transfer tokens
     *
     * Send `_value` tokens to `_to` from your account
     *
     * @param _to The address of the recipient
     * @param _value the amount to send
     */
    function transfer(address _to, uint256 _value) public returns (bool success) {
        _transfer(msg.sender, _to, _value);
        return true;
    }

    /**
     * Transfer tokens from other address
     *
     * Send `_value` tokens to `_to` on behalf of `_from`
     *
     * @param _from The address of the sender
     * @param _to The address of the recipient
     * @param _value the amount to send
     */
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        require(_value <= allowance[_from][msg.sender]);     // Check allowance
        allowance[_from][msg.sender] -= _value;
        _transfer(_from, _to, _value);
        return true;
    }

    /**
     * Set allowance for other address
     *
     * Allows `_spender` to spend no more than `_value` tokens on your behalf
     *
     * @param _spender The address authorized to spend
     * @param _value the max amount they can spend
     */
    function approve(address _spender, uint256 _value) public
        returns (bool success) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    /**
     * Set allowance for other address and notify
     *
     * Allows `_spender` to spend no more than `_value` tokens on your behalf, and then ping the contract about it
     *
     * @param _spender The address authorized to spend
     * @param _value the max amount they can spend
     * @param _extraData some extra information to send to the approved contract
     */
    function approveAndCall(address _spender, uint256 _value, bytes _extraData)
        public
        returns (bool success) {
        tokenRecipient spender = tokenRecipient(_spender);
        if (approve(_spender, _value)) {
            spender.receiveApproval(msg.sender, _value, this, _extraData);
            return true;
        }
    }

    /**
     * Destroy tokens
     *
     * Remove `_value` tokens from the system irreversibly
     *
     * @param _value the amount of money to burn
     */
    function burn(uint256 _value) public returns (bool success) {
        require(balanceOf[msg.sender] >= _value);   // Check if the sender has enough
        balanceOf[msg.sender] -= _value;            // Subtract from the sender
        totalSupply -= _value;                      // Updates totalSupply
        emit Burn(msg.sender, _value);
        return true;
    }

    /**
     * Destroy tokens from other account
     *
     * Remove `_value` tokens from the system irreversibly on behalf of `_from`.
     *
     * @param _from the address of the sender
     * @param _value the amount of money to burn
     */
    function burnFrom(address _from, uint256 _value) public returns (bool success) {
        require(balanceOf[_from] >= _value);                // Check if the targeted balance is enough
        require(_value <= allowance[_from][msg.sender]);    // Check allowance
        balanceOf[_from] -= _value;                         // Subtract from the targeted balance
        allowance[_from][msg.sender] -= _value;             // Subtract from the sender's allowance
        totalSupply -= _value;                              // Update totalSupply
        emit Burn(_from, _value);
        return true;
    }
}
'''

compiled_sol = compile_source(ERC20) # Compiled source code
contract_interface = compiled_sol['<stdin>:TokenERC20']
w3.eth.defaultAccount = w3.eth.accounts[0]
ERC20_deployed = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

tx_hash = ERC20_deployed.constructor(100000000, "PEWPEW", "PEW").transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

tx_hash2 = ERC20_deployed.constructor(100000000, "LOOT", "LOOT").transact()
tx_receipt2 = w3.eth.waitForTransactionReceipt(tx_hash2)


print("ERC20 PEWPEW Created: " + tx_receipt.contractAddress)
print("ERC20 LOOT Created: " + tx_receipt2.contractAddress)
# Create the contract instance with the newly-deployed address
erc20_instance = w3.eth.contract(
    address=tx_receipt.contractAddress,
    abi=contract_interface['abi'],
)

erc20_loot_instance = w3.eth.contract(
    address=tx_receipt2.contractAddress,
    abi=contract_interface['abi'],
)

# Create Vaults
print("Creating Valut(s)")
#market_contract.fallback.transact({'from': w3.eth.accounts[1], 'gas': 6021975, 'value': 0})
#market_contract.fallback.transact({'from': w3.eth.accounts[2], 'gas': 6021975, 'value': 0})

vault_address = market_contract.functions.my_vault().call({'from': w3.eth.accounts[1]})
vault_address2 = market_contract.functions.my_vault().call({'from': w3.eth.accounts[2]})
print("Vault(s) Created: " + vault_address + ", " + vault_address2)

# Give out tokens to addresses 2 & 3
print("Giving accounts[1]'s Vault 200000 PEW")
erc20_instance.functions.transfer(vault_address, 200000).transact()
print("Giving accounts[2]'s Vault 200000 PEW")
erc20_instance.functions.transfer(vault_address2, 200000).transact()

print("Giving accounts[1]'s Vault 200000 LOOT")
erc20_loot_instance.functions.transfer(vault_address, 200000).transact()
print("Giving accounts[2]'s Vault 200000 LOOT")
erc20_loot_instance.functions.transfer(vault_address2, 200000).transact()

print("Checking token balances (PEW)...")
accounts2_bal = erc20_instance.call().balanceOf(vault_address)
print("Accounts[2] Vault: " + str(accounts2_bal))
accounts3_bal = erc20_instance.call().balanceOf(vault_address2)
print("Accounts[3] Vault: " + str(accounts3_bal))

print("Checking token balances (LOOT)...")
accounts2_bal = erc20_loot_instance.call().balanceOf(vault_address)
print("Accounts[2] Vault: " + str(accounts2_bal))
accounts3_bal = erc20_loot_instance.call().balanceOf(vault_address2)
print("Accounts[3] Vault: " + str(accounts3_bal))

# account 2 create three listings
#listing_1 = market_contract.functions.create_listing("0x9C8f1226c1732Fb0a658636FA654B32747002887", 3, 200).transact({'from': w3.eth.accounts[1]})
#listing_2 = market_contract.functions.create_listing("0x25c238210aa867aEE262155E0774b43621dcd42B", 1, 5000).transact({'from': w3.eth.accounts[1]})
#listing_3 = market_contract.functions.create_listing("0x58a8a50e1AA9e2B82959E8Ca8a50A945052ACF5E", 1, 3300).transact({'from': w3.eth.accounts[1]})

# account 3 fulfill one of the listings



# create listings and fulfill them over time randomly until tokens run out