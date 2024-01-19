/**
 *Submitted for verification at Etherscan.io on 2019-08-10
*/

/**
 * SEED Platform DEX
 */

pragma solidity ^0.5.2;


/**
 * @title ERC20 interface
 * @dev see https://eips.ethereum.org/EIPS/eip-20
 */
interface IERC20 {
    function transfer(address to, uint256 value) external returns (bool);

    function approve(address spender, uint256 value) external returns (bool);

    function transferFrom(address from, address to, uint256 value) external returns (bool);

    function totalSupply() external view returns (uint256);

    function balanceOf(address who) external view returns (uint256);

    function allowance(address owner, address spender) external view returns (uint256);

    function okToTransferTokens(address _holder, uint256 _amountToAdd) external view returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);

    event Approval(address indexed owner, address indexed spender, uint256 value);
}


/**
 * @title SafeMath
 * @dev Unsigned math operations with safety checks that revert on error.
 */
library SafeMath {
    /**
     * @dev Multiplies two unsigned integers, reverts on overflow.
     */
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
        // benefit is lost if 'b' is also tested.
        // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
        if (a == 0) {
            return 0;
        }

        uint256 c = a * b;
        require(c / a == b, "SafeMath: multiplication overflow");

        return c;
    }

    /**
     * @dev Integer division of two unsigned integers truncating the quotient, reverts on division by zero.
     */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // Solidity only automatically asserts when dividing by 0
        require(b > 0, "SafeMath: division by zero");
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold

        return c;
    }

    /**
     * @dev Subtracts two unsigned integers, reverts on overflow (i.e. if subtrahend is greater than minuend).
     */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a, "SafeMath: subtraction overflow");
        uint256 c = a - b;

        return c;
    }

    /**
     * @dev Adds two unsigned integers, reverts on overflow.
     */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "SafeMath: addition overflow");

        return c;
    }

    /**
     * @dev Divides two unsigned integers and returns the remainder (unsigned integer modulo),
     * reverts when dividing by zero.
     */
    function mod(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b != 0, "SafeMath: modulo by zero");
        return a % b;
    }
}


interface IFactory {
    function changeATFactoryAddress(address) external;
    function changeTDeployerAddress(address) external;
    function changeFPDeployerAddress(address) external;
    function changeDeployFees (uint256) external;
    function changeFeesCollector (address) external;
    function deployPanelContracts(string calldata, string calldata, string calldata, bytes32, uint8, uint8, uint8, uint256) external;
    function getTotalDeployFees() external view returns (uint256);
    function isFactoryDeployer(address) external view returns(bool);
    function isFactoryATGenerated(address) external view returns(bool);
    function isFactoryTGenerated(address) external view returns(bool);
    function isFactoryFPGenerated(address) external view returns(bool);
    function getTotalDeployer() external view returns(uint256);
    function getTotalATContracts() external view returns(uint256);
    function getTotalTContracts() external view returns(uint256);
    function getTotalFPContracts() external view returns(uint256);
    function getContractsByIndex(uint256) external view returns (address, address, address, address);
    function getDeployerAddressByIndex(uint256) external view returns (address);
    function getATAddressByIndex(uint256) external view returns (address);
    function getTAddressByIndex(uint256) external view returns (address);
    function getFPAddressByIndex(uint256) external view returns (address);
    function withdraw(address) external;
}


/**
 * @title SeedDex
 * @dev This is the main contract for the Seed Decentralised Exchange.
 */
contract SeedDex {

  using SafeMath for uint;

  /// Variables
  address public seedToken; // the seed token
  address public factoryAddress; // Address of the factory
  address private ethAddress = address(0);

  // True when Token.transferFrom is being called from depositToken
  bool private depositingTokenFlag;

  // mapping of token addresses to mapping of account balances (token=0 means Ether)
  mapping (address => mapping (address => uint)) private tokens;

  // mapping of user accounts to mapping of order hashes to booleans (true = submitted by user, equivalent to offchain signature)
  mapping (address => mapping (bytes32 => bool)) private orders;

  // mapping of user accounts to mapping of order hashes to uints (amount of order that has been filled)
  mapping (address => mapping (bytes32 => uint)) private orderFills;

  /// Logging Events
  event Order(address tokenGet, uint amountGet, address tokenGive, uint amountGive, uint expires, uint nonce, address user);
  event Cancel(address tokenGet, uint amountGet, address tokenGive, uint amountGive, uint expires, uint nonce, address user, uint8 v, bytes32 r, bytes32 s);
  event Trade(address tokenGet, uint amountGet, address tokenGive, uint amountGive, address get, address give);
  event Deposit(address token, address user, uint amount, uint balance);
  event Withdraw(address token, address user, uint amount, uint balance);

  /// Constructor function. This is only called on contract creation.
  constructor(address _seedToken, address _factoryAddress)  public {
    seedToken = _seedToken;
    factoryAddress = _factoryAddress;
    depositingTokenFlag = false;
  }

  /// The fallback function. Ether transfered into the contract is not accepted.
  function() external {
    revert("ETH not accepted!");
  }

  ////////////////////////////////////////////////////////////////////////////////
  // Deposits, Withdrawals, Balances
  ////////////////////////////////////////////////////////////////////////////////


  /**
  * This function handles deposits of Ether into the contract.
  * Emits a Deposit event.
  * Note: With the payable modifier, this function accepts Ether.
  */
  function deposit() public payable {
    tokens[ethAddress][msg.sender] = tokens[ethAddress][msg.sender].add(msg.value);
    emit Deposit(ethAddress, msg.sender, msg.value, tokens[ethAddress][msg.sender]);
  }

  /**
  * This function handles withdrawals of Ether from the contract.
  * Verifies that the user has enough funds to cover the withdrawal.
  * Emits a Withdraw event.
  * @param amount uint of the amount of Ether the user wishes to withdraw
  */
  function withdraw(uint amount) public {
    require(tokens[ethAddress][msg.sender] >= amount, "Not enough balance");
    tokens[ethAddress][msg.sender] = tokens[ethAddress][msg.sender].sub(amount);
    msg.sender.transfer(amount);
    emit Withdraw(ethAddress, msg.sender, amount, tokens[ethAddress][msg.sender]);
  }
  
  /**
  * This function handles deposits of Ethereum based tokens to the contract.
  * Does not allow Ether.
  * If token transfer fails, transaction is reverted and remaining gas is refunded.
  * Emits a Deposit event.
  * Note: Remember to call Token(address).approve(this, amount) or this contract will not be able to do the transfer on your behalf.
  * @param token Ethereum contract address of the token or 0 for Ether
  * @param amount uint of the amount of the token the user wishes to deposit
  */
  function depositToken(address token, uint amount) public {
    require(token != ethAddress, "Seed: expecting the zero address to be ERC20");
    require(IFactory(factoryAddress).isFactoryTGenerated(token) || token == seedToken, "Seed: deposit allowed only for known tokens");

    depositingTokenFlag = true;
    IERC20(token).transferFrom(msg.sender, address(this), amount);
    depositingTokenFlag = false;
    tokens[token][msg.sender] = tokens[token][msg.sender].add(amount);
    emit Deposit(token, msg.sender, amount, tokens[token][msg.sender]);
  }


  
  /**
  * This function handles withdrawals of Ethereum based tokens from the contract.
  * Does not allow Ether.
  * If token transfer fails, transaction is reverted and remaining gas is refunded.
  * Emits a Withdraw event.
  * @param token Ethereum contract address of the token or 0 for Ether
  * @param amount uint of the amount of the token the user wishes to withdraw
  */
  function withdrawToken(address token, uint amount) public {
    require(token != ethAddress, "Seed: expecting the zero address to be ERC20");
    require(tokens[token][msg.sender] >= amount, "Not enough balance");

    tokens[token][msg.sender] = tokens[token][msg.sender].sub(amount);
    require(IERC20(token).transfer(msg.sender, amount), "Transfer failed");
    emit Withdraw(token, msg.sender, amount, tokens[token][msg.sender]);
  }

  /**
  * Retrieves the balance of a token based on a user address and token address.
  * @param token Ethereum contract address of the token or 0 for Ether
  * @param user Ethereum address of the user
  * @return the amount of tokens on the exchange for a given user address
  */
  function balanceOf(address token, address user) public view returns (uint) {
    return tokens[token][user];
  }

  ////////////////////////////////////////////////////////////////////////////////
  // Trading
  ////////////////////////////////////////////////////////////////////////////////

  /**
  * Stores the active order inside of the contract.
  * Emits an Order event.
  * Note: tokenGet & tokenGive can be the Ethereum contract address.
  * @param tokenGet Ethereum contract address of the token to receive
  * @param amountGet uint amount of tokens being received
  * @param tokenGive Ethereum contract address of the token to give
  * @param amountGive uint amount of tokens being given
  * @param expires uint of block number when this order should expire
  * @param nonce arbitrary random number
  */
  function order(address tokenGet, uint amountGet, address tokenGive, uint amountGive, uint expires, uint nonce) public {
    require(isValidPair(tokenGet, tokenGive), "Not a valid pair");
    require(canBeTransferred(tokenGet, msg.sender, amountGet), "Token quota exceeded");
    bytes32 hash = sha256(abi.encodePacked(this, tokenGet, amountGet, tokenGive, amountGive, expires, nonce));
    orders[msg.sender][hash] = true;
    emit Order(tokenGet, amountGet, tokenGive, amountGive, expires, nonce, msg.sender);
  }

  /**
  * Facilitates a trade from one user to another.
  * Requires that the transaction is signed properly, the trade isn't past its expiration, and all funds are present to fill the trade.
  * Calls tradeBalances().
  * Updates orderFills with the amount traded.
  * Emits a Trade event.
  * Note: tokenGet & tokenGive can be the Ethereum contract address.
  * Note: amount is in amountGet / tokenGet terms.
  * @param tokenGet Ethereum contract address of the token to receive
  * @param amountGet uint amount of tokens being received
  * @param tokenGive Ethereum contract address of the token to give
  * @param amountGive uint amount of tokens being given
  * @param expires uint of block number when this order should expire
  * @param nonce arbitrary random number
  * @param user Ethereum address of the user who placed the order
  * @param v part of signature for the order hash as signed by user
  * @param r part of signature for the order hash as signed by user
  * @param s part of signature for the order hash as signed by user
  * @param amount uint amount in terms of tokenGet that will be "buy" in the trade
  */
  function trade(
        address  tokenGet,
        uint     amountGet,
        address  tokenGive,
        uint     amountGive,
        uint     expires,
        uint     nonce,
        address  user,
        uint8    v,
        bytes32  r,
        bytes32  s,
        uint     amount) public {
    require(isValidPair(tokenGet, tokenGive), "Not a valid pair");
    require(canBeTransferred(tokenGet, msg.sender, amountGet), "Token quota exceeded");
    bytes32 hash = sha256(abi.encodePacked(this, tokenGet, amountGet, tokenGive, amountGive, expires, nonce));
    bytes32 m = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    /*require((
      (orders[user][hash] || ecrecover(m, v, r, s) == user) &&
      block.number <= expires &&
      orderFills[user][hash].add(amount) <= amountGet
    ));*/
    require(orders[user][hash] || ecrecover(m, v, r, s) == user, "Order does not exist");
    require(block.number <= expires, "Order Expired");
    require(orderFills[user][hash].add(amount) <= amountGet, "Order amount exceeds maximum availability");
    tradeBalances(tokenGet, amountGet, tokenGive, amountGive, user, amount);
    orderFills[user][hash] = orderFills[user][hash].add(amount);
    uint amt = amountGive.mul(amount) / amountGet;
    emit Trade(tokenGet, amount, tokenGive, amt, user, msg.sender);
  }

  /**
  * This is a private function and is only being called from trade().
  * Handles the movement of funds when a trade occurs.
  * Takes fees.
  * Updates token balances for both buyer and seller.
  * Note: tokenGet & tokenGive can be the Ethereum contract address.
  * Note: amount is in amountGet / tokenGet terms.
  * @param tokenGet Ethereum contract address of the token to receive
  * @param amountGet uint amount of tokens being received
  * @param tokenGive Ethereum contract address of the token to give
  * @param amountGive uint amount of tokens being given
  * @param user Ethereum address of the user who placed the order
  * @param amount uint amount in terms of tokenGet that will be "buy" in the trade
  */
  function tradeBalances(address tokenGet, uint amountGet, address tokenGive, uint amountGive, address user, uint amount) private {
    tokens[tokenGet][msg.sender] = tokens[tokenGet][msg.sender].sub(amount);
    tokens[tokenGet][user] = tokens[tokenGet][user].add(amount);
    tokens[tokenGive][user] = tokens[tokenGive][user].sub(amountGive.mul(amount).div(amountGet));
    tokens[tokenGive][msg.sender] = tokens[tokenGive][msg.sender].add(amountGive.mul(amount).div(amountGet));
  }

  /**
  * This function is to test if a trade would go through.
  * Note: tokenGet & tokenGive can be the Ethereum contract address.
  * Note: amount is in amountGet / tokenGet terms.
  * @param tokenGet Ethereum contract address of the token to receive
  * @param amountGet uint amount of tokens being received
  * @param tokenGive Ethereum contract address of the token to give
  * @param amountGive uint amount of tokens being given
  * @param expires uint of block number when this order should expire
  * @param nonce arbitrary random number
  * @param user Ethereum address of the user who placed the order
  * @param v part of signature for the order hash as signed by user
  * @param r part of signature for the order hash as signed by user
  * @param s part of signature for the order hash as signed by user
  * @param amount uint amount in terms of tokenGet that will be "buy" in the trade
  * @param sender Ethereum address of the user taking the order
  * @return bool: true if the trade would be successful, false otherwise
  */
  function testTrade(address tokenGet, uint amountGet, address tokenGive, uint amountGive, uint expires, uint nonce, address user, uint8 v, bytes32 r, bytes32 s, uint amount, address sender) public view returns(bool) {
    if (tokens[tokenGet][sender] < amount) return false;
    if (availableVolume(tokenGet, amountGet, tokenGive, amountGive, expires, nonce, user, v, r, s) < amount) return false;
    if (!canBeTransferred(tokenGet, msg.sender, amountGet)) return false;

    return true;
  }

  function canBeTransferred(address token, address user, uint newAmt) private view returns(bool) {
    return (token == seedToken || IERC20(token).okToTransferTokens(user, newAmt + tokens[token][user]) ) ;
  }

  /**
  * This function checks the available volume for a given order.
  * Note: tokenGet & tokenGive can be the Ethereum contract address.
  * @param tokenGet Ethereum contract address of the token to receive
  * @param amountGet uint amount of tokens being received
  * @param tokenGive Ethereum contract address of the token to give
  * @param amountGive uint amount of tokens being given
  * @param expires uint of block number when this order should expire
  * @param nonce arbitrary random number
  * @param user Ethereum address of the user who placed the order
  * @param v part of signature for the order hash as signed by user
  * @param r part of signature for the order hash as signed by user
  * @param s part of signature for the order hash as signed by user
  * @return uint: amount of volume available for the given order in terms of amountGet / tokenGet
  */
  function availableVolume(
          address tokenGet,
          uint amountGet,
          address tokenGive,
          uint amountGive,
          uint expires,
          uint nonce,
          address user,
          uint8 v,
          bytes32 r,
          bytes32 s
  ) public view returns(uint) {

    bytes32 hash = sha256(abi.encodePacked(this, tokenGet, amountGet, tokenGive, amountGive, expires, nonce));

    if ( (orders[user][hash] || ecrecover(keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash)), v, r, s) == user) || block.number <= expires ) {
      return 0;
    }

    uint[2] memory available;
    available[0] = amountGet.sub(orderFills[user][hash]);

    available[1] = tokens[tokenGive][user].mul(amountGet) / amountGive;

    if (available[0] < available[1]) {
      return available[0];
    } else {
      return available[1];
    }

  }

  /**
  * This function checks the amount of an order that has already been filled.
  * Note: tokenGet & tokenGive can be the Ethereum contract address.
  * @param tokenGet Ethereum contract address of the token to receive
  * @param amountGet uint amount of tokens being received
  * @param tokenGive Ethereum contract address of the token to give
  * @param amountGive uint amount of tokens being given
  * @param expires uint of block number when this order should expire
  * @param nonce arbitrary random number
  * @param user Ethereum address of the user who placed the order
  * @return uint: amount of the given order that has already been filled in terms of amountGet / tokenGet
  */
  /* @param v part of signature for the order hash as signed by user
  * @param r part of signature for the order hash as signed by user
  * @param s part of signature for the order hash as signed by user */
  function amountFilled(
          address tokenGet,
          uint amountGet,
          address tokenGive,
          uint amountGive,
          uint expires,
          uint nonce,
          address user/*,
          uint8 v,
          bytes32 r,
          bytes32 s*/
  ) public view returns(uint) {
    bytes32 hash = sha256(abi.encodePacked(this, tokenGet, amountGet, tokenGive, amountGive, expires, nonce));
    return orderFills[user][hash];
  }

  /**
  * This function cancels a given order by editing its fill data to the full amount.
  * Requires that the transaction is signed properly.
  * Updates orderFills to the full amountGet
  * Emits a Cancel event.
  * Note: tokenGet & tokenGive can be the Ethereum contract address.
  * @param tokenGet Ethereum contract address of the token to receive
  * @param amountGet uint amount of tokens being received
  * @param tokenGive Ethereum contract address of the token to give
  * @param amountGive uint amount of tokens being given
  * @param expires uint of block number when this order should expire
  * @param nonce arbitrary random number
  * @param v part of signature for the order hash as signed by user
  * @param r part of signature for the order hash as signed by user
  * @param s part of signature for the order hash as signed by user
  * @return uint: amount of the given order that has already been filled in terms of amountGet / tokenGet
  */
  function cancelOrder(address tokenGet, uint amountGet, address tokenGive, uint amountGive, uint expires, uint nonce, uint8 v, bytes32 r, bytes32 s) public {
    bytes32 hash = sha256(abi.encodePacked(this, tokenGet, amountGet, tokenGive, amountGive, expires, nonce));
    bytes32 m = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", hash));
    require(orders[msg.sender][hash] || ecrecover(m, v, r, s) == msg.sender, "Order does not exist");
    orderFills[msg.sender][hash] = amountGet;
    emit Cancel(tokenGet, amountGet, tokenGive, amountGive, expires, nonce, msg.sender, v, r, s);
  }
                                                
  /**
  * this function check if the given pair is valid.
  * @param tokenGet ethereum contract address of the token to receive
  * @param tokenGive ethereum contract address of the token to give
  * @return bool: return true if given pair is valid, otherwise false.
  */
  function isValidPair(address tokenGet, address tokenGive) private view returns(bool) {
     if( isEthSeedPair(tokenGet, tokenGive) ) return true;
     return isSeedPair(tokenGet, tokenGive);
  }

  /**
  * this function check if the given pair is ETH-SEED or SEED-ETH.
  * @param tokenGet ethereum contract address of the token to receive
  * @param tokenGive ethereum contract address of the token to give
  * @return bool: return true if it's either ETH-SEED or SEED-ETH, otherwise false.
  */
  function isEthSeedPair(address tokenGet, address tokenGive) private view returns(bool) {
      if (tokenGet == ethAddress && tokenGive == seedToken) return true;
      if (tokenGet == seedToken && tokenGive == ethAddress) return true;
      return false;
  }

  /**
  * this function check if the given pair of tokens include the seed native token.
  * @param tokenGet ethereum contract address of the token to receive
  * @param tokenGive ethereum contract address of the token to give
  * @return bool: return true if one of the token is seed, otherwise false.
  */
  function isSeedPair(address tokenGet, address tokenGive) private view returns(bool) {
      if (tokenGet == tokenGive) return false;
      if (tokenGet == seedToken) return true;
      if (tokenGive == seedToken) return true;
      return false;
  }
}