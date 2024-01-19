/**
 *Submitted for verification at Etherscan.io on 2019-08-11
*/

/**
 *Submitted for verification at Etherscan.io on 2019-08-09
*/

pragma solidity 0.4.25;

/**
 * @title SafeMath
 * @dev Math operations with safety checks that revert on error
 */
library SafeMath {

  /**
  * @dev Multiplies two numbers, reverts on overflow.
  */
  function mul(uint256 a, uint256 b) internal pure returns (uint256) {
    // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
    // benefit is lost if 'b' is also tested.
    // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
    if (a == 0) {
      return 0;
    }

    uint256 c = a * b;
    require(c / a == b);

    return c;
  }

  /**
  * @dev Integer division of two numbers truncating the quotient, reverts on division by zero.
  */
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b > 0); // Solidity only automatically asserts when dividing by 0
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold

    return c;
  }

  /**
  * @dev Subtracts two numbers, reverts on overflow (i.e. if subtrahend is greater than minuend).
  */
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b <= a);
    uint256 c = a - b;

    return c;
  }

  /**
  * @dev Adds two numbers, reverts on overflow.
  */
  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    require(c >= a);

    return c;
  }

  /**
  * @dev Divides two numbers and returns the remainder (unsigned integer modulo),
  * reverts when dividing by zero.
  */
  function mod(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b != 0);
    return a % b;
  }
}

/**
 * @title Roles
 * @dev Library for managing addresses assigned to a Role.
 */
library Roles {
  struct Role {
    mapping (address => bool) bearer;
  }

  /**
   * @dev give an account access to this role
   */
  function add(Role storage role, address account) internal {
    require(account != address(0));
    require(!has(role, account));

    role.bearer[account] = true;
  }

  /**
   * @dev remove an account's access to this role
   */
  function remove(Role storage role, address account) internal {
    require(account != address(0));
    require(has(role, account));

    role.bearer[account] = false;
  }

  /**
   * @dev check if an account has this role
   * @return bool
   */
  function has(Role storage role, address account)
    internal
    view
    returns (bool)
  {
    require(account != address(0));
    return role.bearer[account];
  }
}

/**
 * @title owned
 * @dev The Ownable contract has an owner address, and provides basic authorization control
 * functions, this simplifies the implementation of "user permissions".
 */
contract owned{
  address private _owner;

  event OwnershipTransferred(
    address indexed previousOwner,
    address indexed newOwner
  );

  /**
   * @dev The Ownable constructor sets the original `owner` of the contract to the sender
   * account.
   */
  constructor() internal {
    _owner = msg.sender;
    emit OwnershipTransferred(address(0), _owner);
  }

  /**
   * @return the address of the owner.
   */
  function owner() public view returns(address) {
    return _owner;
  }

  /**
   * @dev Throws if called by any account other than the owner.
   */
  modifier onlyOwner() {
    require(isOwner());
    _;
  }

  /**
   * @return true if `msg.sender` is the owner of the contract.
   */
  function isOwner() public view returns(bool) {
    return msg.sender == _owner;
  }

  /**
   * @dev Allows the current owner to relinquish control of the contract.
   * @notice Renouncing to ownership will leave the contract without an owner.
   * It will not be possible to call the functions with the `onlyOwner`
   * modifier anymore.
   */
  function renounceOwnership() public onlyOwner {
    emit OwnershipTransferred(_owner, address(0));
    _owner = address(0);
  }

  /**
   * @dev Allows the current owner to transfer control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) public onlyOwner {
    _transferOwnership(newOwner);
  }

  /**
   * @dev Transfers control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function _transferOwnership(address newOwner) internal {
    require(newOwner != address(0));
    emit OwnershipTransferred(_owner, newOwner);
    _owner = newOwner;
  }
}

interface ERC20Interface {
   
    function balanceOf(address who) constant external returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    event Transfer(address indexed from, address indexed to, uint256 value);
}

contract ERC20 is ERC20Interface{
    function allowance(address owner, address spender) public constant returns (uint256);
    function transferFrom(address from, address to, uint256 value) public returns (bool);
    function approve(address spender, uint256 value) public returns (bool);
    function burn(uint256 _value) public ;
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

library SafeERC20 {


  function safeTransfer(ERC20 token, address to, uint256 value) internal {
    assert(token.transfer(to, value));
  }

  function safeTransferFrom(ERC20 token, address from, address to, uint256 value) internal {
    assert(token.transferFrom(from, to, value));
  }

  function safeApprove(ERC20 token, address spender, uint256 value) internal {
    assert(token.approve(spender, value));
  }
}

contract ConverterRole {
  using Roles for Roles.Role;

  event ConverterAdded(address indexed account);
  event ConverterRemoved(address indexed account);

  Roles.Role private converters;

  constructor() internal {
    _addConverter(msg.sender);
  }

  modifier onlyConverter() {
    require(isConverter(msg.sender));
    _;
  }

  function isConverter(address account) public view returns (bool) {
    return converters.has(account);
  }

  function addConverter(address account) public onlyConverter {
    _addConverter(account);
  }

  function renounceConverter() public {
    _removeConverter(msg.sender);
  }

  function _addConverter(address account) internal {
    converters.add(account);
    emit ConverterAdded(account);
  }

  function _removeConverter(address account) internal {
    converters.remove(account);
    emit ConverterRemoved(account);
  }
}
contract CoinDumper is owned{
    //In this contract the dumped ERC20 coins can not be accessable, they will be locked in this contract forever
    function withdrawEtherFromcontract(uint _amountInwei) public onlyOwner{
      require(address(this).balance > _amountInwei);
      require(isOwner());
      msg.sender.transfer(_amountInwei);
      
    }
    
}
contract ConvertButterCoinToEther is owned, ConverterRole{
    
    using SafeERC20 for ERC20;
    using SafeMath for uint256;
    uint256 private buttercoinToEth_conversion_rate;
    ERC20 ButterCoin;
    CoinDumper public dumpercontract;
    
    constructor() public
     {
         
         ButterCoin = ERC20(0x0A45226f078Eb78bF8FCc95a6e2FFf55243A4CE6);
         buttercoinToEth_conversion_rate = 1; // 1 smallest unit of BTTR = 1 wei OR 1 BTTR = 1 ETH (1:1)
         dumpercontract = new CoinDumper(); // The coinDumper contract created
     }
    
    function() public payable {
         //not payable fallback function
          
    }
    function close() public onlyOwner { //onlyOwner is custom modifier
  selfdestruct(msg.sender);  // `owner` is the owners address
}
    function setConversionRate(uint256 _valueInWei) public onlyOwner returns (uint256){
        //set value of the smallest unit of buttercoin in wei
        require(_valueInWei >= 0);
         buttercoinToEth_conversion_rate = _valueInWei;
        return  buttercoinToEth_conversion_rate;
    }
    function getConversionRate() public view returns(uint256 _rate){
        
        return buttercoinToEth_conversion_rate;
    }
    function convertButterCointoEther(uint256 value) public onlyConverter{
        require(value <= ButterCoin.balanceOf(address(this)), "No ButterCoin in contract available for conversion");
        ButterCoin.safeTransfer(address(dumpercontract),value);
        if(buttercoinToEth_conversion_rate > 0)
        {
            uint256 equivalent_wei = value.mul(getConversionRate());
            require(address(this).balance >= equivalent_wei, "There's no ETH in the contract");
            msg.sender.transfer(equivalent_wei);
        }
    }
     
    function withdrawEtherFromcontract(uint _amountInwei) public onlyOwner{
      require(address(this).balance > _amountInwei);
      require(isOwner());
      msg.sender.transfer(_amountInwei);
      
    }
    
    function withdrawTokenFromcontract(ERC20 _token, uint256 _tamount) public onlyOwner{
        require(_token.balanceOf(address(this)) > _tamount);
         _token.safeTransfer(msg.sender, _tamount);
     
    }
    
}