/**
 *Submitted for verification at Etherscan.io on 2019-08-12
*/

pragma solidity >=0.5; 


/**
 * @title Ownable
 * @dev The Ownable contract has an owner address, and provides basic authorization control
 * functions, this simplifies the implementation of "user permissions".
 */
contract Ownable {
  address public owner;


  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);


  /**
   * @dev The Ownable constructor sets the original `owner` of the contract to the sender
   * account.
   */
  constructor() public {
    owner = tx.origin;
  }


  /**
   * @dev Throws if called by any account other than the owner.
   */
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }


  /**
   * @dev Allows the current owner to transfer control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    emit OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

}


/**
 * @title IGasStorage
 * @dev  GasStorage interface to burn and mint gastoken
 */
interface IGasStorage
{
    function mint(uint256 value) external;
    function burn(uint256 value) external;
    function balanceOf() external view returns (uint256 balance);
} 

/**
 * @title GasToken
 * @dev  GasToken
 */
interface GasToken
{
     function mint(uint256 value) external;
     function free(uint256 value) external;
     function freeUpTo(uint256 value) external returns (uint256 freed);
     function balanceOf(address owner) external view returns (uint256 balance);
     function transfer(address to, uint256 value) external returns (bool success);
} 

/**
 * @title GasStorage
 * @dev  GasStrorage contract to mint and burn gastoken to save the gas at each transaction
 */ 
contract GasStorage is IGasStorage,Ownable
{
    address _dex; 
    address _gasToken;

    uint256 _baseBurn;
    uint256 _eachBurnBase;

    event GasStatus(uint256 gasLeft,uint256 gasUsed);
    event GasMined(address miner,uint256 mineAmount);

    modifier onlyDex {
        if (msg.sender != _dex ) return;
        _;
    }  

    constructor(address dex,address gasToken) public {
        _dex = dex;   
        _gasToken = gasToken;
        _baseBurn = 15000;
        _eachBurnBase = 20000;
    }  

    function setDex(address dex) public onlyOwner{
        _dex = dex;
    }

    function setGasToken(address gasToken) public onlyOwner{
        _gasToken = gasToken;
    } 
 
    function setBaseBurn(uint256 baseBurn) public onlyOwner{
        _baseBurn = baseBurn;
    }
 
   /**
   * @dev  setEachBurnBase
   * @param eachBurnBase  gt1 = 20000, gt2 = 48000
   */
    function setEachBurnBase(uint256 eachBurnBase) public onlyOwner{
        _eachBurnBase = eachBurnBase;
    }

   /**
   * @dev  mint gas token
   * @param value  the value to mint
   */
    function mint(uint256 value)  public
    {
        if( _gasToken != address(0))
        { 
            GasToken(_gasToken).mint(value); 
            emit GasMined(msg.sender,value);
        }
    } 
 
   /**
   * @dev  burn the gas token to save the gas.
   * @param value  the value to save , 1 value ≈ 10000 gas  
   */
    function burn(uint256 value) public onlyDex
    {
        if( _gasToken == address(0))
        {
            return;
        } 

        if(GasToken(_gasToken).balanceOf(address(this)) == 0){
            return;
        } 

        uint256 gasLeftSaved = gasleft();
        emit GasStatus(gasLeftSaved,value);

        uint256 burnNumber = (value + _baseBurn) / _eachBurnBase;
 
        GasToken(_gasToken).freeUpTo(burnNumber); 

        emit GasStatus(gasleft(), gasLeftSaved - gasleft());
    }

   /**
   * @dev  balanceOf. 
   * @return balance Of msg.sender
   */
    function balanceOf() public view returns (uint256 balance)
    {
        if( _gasToken != address(0))
        {
            return GasToken(_gasToken).balanceOf(address(this));
        } 

        return 0;
    }

   /**
   * @dev transfer to a user.
   * @param to The address to transfer to.
   * @param amount The amount to transfer.
   */
    function transfer(address to,uint256 amount) public onlyOwner{

        if( _gasToken == address(0))
        {
            return;
        } 

        GasToken(_gasToken).transfer(to,amount);
    }
}