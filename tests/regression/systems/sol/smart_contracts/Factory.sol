/**
 *Submitted for verification at Etherscan.io on 2019-08-10
*/

/**
 * SEED Platform Factory
 */

pragma solidity ^0.5.2;


/**
 * @title Ownable
 * @dev The Ownable contract has an owner address, and provides basic authorization control
 * functions, this simplifies the implementation of "user permissions".
 */
contract Ownable {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev The Ownable constructor sets the original `owner` of the contract to the sender
     * account.
     */
    constructor () internal {
        _owner = msg.sender;
        emit OwnershipTransferred(address(0), _owner);
    }

    /**
     * @return the address of the owner.
     */
    function owner() public view returns (address) {
        return _owner;
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier onlyOwner() {
        require(isOwner(), "Not Owner!");
        _;
    }

    /**
     * @return true if `msg.sender` is the owner of the contract.
     */
    function isOwner() public view returns (bool) {
        return msg.sender == _owner;
    }

    /**
     * @dev Allows the current owner to relinquish control of the contract.
     * It will not be possible to call the functions with the `onlyOwner`
     * modifier anymore.
     * @notice Renouncing ownership will leave the contract without an owner,
     * thereby removing any functionality that is only available to the owner.
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
        require(newOwner != address(0),"Address 0 could not be owner");
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }
}


/**
 * @dev Wrappers over Solidity's arithmetic operations with added overflow
 * checks.
 *
 * Arithmetic operations in Solidity wrap on overflow. This can easily result
 * in bugs, because programmers usually assume that an overflow raises an
 * error, which is the standard behavior in high level programming languages.
 * `SafeMath` restores this intuition by reverting the transaction when an
 * operation overflows.
 *
 * Using this library instead of the unchecked operations eliminates an entire
 * class of bugs, so it's recommended to use it always.
 */
library SafeMath {
    /**
     * @dev Returns the addition of two unsigned integers, reverting on
     * overflow.
     *
     * Counterpart to Solidity's `+` operator.
     *
     * Requirements:
     * - Addition cannot overflow.
     */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "SafeMath: addition overflow");

        return c;
    }

    /**
     * @dev Returns the subtraction of two unsigned integers, reverting on
     * overflow (when the result is negative).
     *
     * Counterpart to Solidity's `-` operator.
     *
     * Requirements:
     * - Subtraction cannot overflow.
     */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a, "SafeMath: subtraction overflow");
        uint256 c = a - b;

        return c;
    }

    /**
     * @dev Returns the multiplication of two unsigned integers, reverting on
     * overflow.
     *
     * Counterpart to Solidity's `*` operator.
     *
     * Requirements:
     * - Multiplication cannot overflow.
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
     * @dev Returns the integer division of two unsigned integers. Reverts on
     * division by zero. The result is rounded towards zero.
     *
     * Counterpart to Solidity's `/` operator. Note: this function uses a
     * `revert` opcode (which leaves remaining gas untouched) while Solidity
     * uses an invalid opcode to revert (consuming all remaining gas).
     *
     * Requirements:
     * - The divisor cannot be zero.
     */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // Solidity only automatically asserts when dividing by 0
        require(b > 0, "SafeMath: division by zero");
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold

        return c;
    }

    /**
     * @dev Returns the remainder of dividing two unsigned integers. (unsigned integer modulo),
     * Reverts when dividing by zero.
     *
     * Counterpart to Solidity's `%` operator. This function uses a `revert`
     * opcode (which leaves remaining gas untouched) while Solidity uses an
     * invalid opcode to revert (consuming all remaining gas).
     *
     * Requirements:
     * - The divisor cannot be zero.
     */
    function mod(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b != 0, "SafeMath: modulo by zero");
        return a % b;
    }
}


interface IERC20Seed {
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);
    function totalSupply() external view returns (uint256);
    function balanceOf(address owner) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function approve(address spender, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}


interface IAdminTools {
    function setFFPAddresses(address, address) external;
    function setMinterAddress(address) external returns(address);
    function getMinterAddress() external view returns(address);
    function getWalletOnTopAddress() external view returns (address);
    function setWalletOnTopAddress(address) external returns(address);

    function addWLManagers(address) external;
    function removeWLManagers(address) external;
    function isWLManager(address) external view returns (bool);
    function addWLOperators(address) external;
    function removeWLOperators(address) external;
    function renounceWLManager() external;
    function isWLOperator(address) external view returns (bool);
    function renounceWLOperators() external;

    function addFundingManagers(address) external;
    function removeFundingManagers(address) external;
    function isFundingManager(address) external view returns (bool);
    function addFundingOperators(address) external;
    function removeFundingOperators(address) external;
    function renounceFundingManager() external;
    function isFundingOperator(address) external view returns (bool);
    function renounceFundingOperators() external;

    function addFundsUnlockerManagers(address) external;
    function removeFundsUnlockerManagers(address) external;
    function isFundsUnlockerManager(address) external view returns (bool);
    function addFundsUnlockerOperators(address) external;
    function removeFundsUnlockerOperators(address) external;
    function renounceFundsUnlockerManager() external;
    function isFundsUnlockerOperator(address) external view returns (bool);
    function renounceFundsUnlockerOperators() external;

    function isWhitelisted(address) external view returns(bool);
    function getWLThresholdBalance() external view returns (uint256);
    function getMaxWLAmount(address) external view returns(uint256);
    function getWLLength() external view returns(uint256);
    function setNewThreshold(uint256) external;
    function changeMaxWLAmount(address, uint256) external;
    function addToWhitelist(address, uint256) external;
    function addToWhitelistMassive(address[] calldata, uint256[] calldata) external returns (bool);
    function removeFromWhitelist(address, uint256) external;
}


interface IATDeployer {
    function newAdminTools(uint256) external returns(address);
    function setFactoryAddress(address) external;
    function getFactoryAddress() external view returns(address);
}


interface ITDeployer {
    function newToken(address, string calldata, string calldata, address) external returns(address);
    function setFactoryAddress(address) external;
    function getFactoryAddress() external view returns(address);
}


interface IFPDeployer {
    function newFundingPanel(address, string calldata, bytes32, uint256, uint256,
                            address, uint256, address, address, uint) external returns(address);
    function setFactoryAddress(address) external;
    function getFactoryAddress() external view returns(address);
}


contract Factory is Ownable {
    using SafeMath for uint256;

    address[] public deployerList;
    uint public deployerLength;
    address[] public ATContractsList;
    address[] public TContractsList;
    address[] public FPContractsList;

    mapping(address => bool) public deployers;
    mapping(address => bool) public ATContracts;
    mapping(address => bool) public TContracts;
    mapping(address => bool) public FPContracts;

    IERC20Seed private seedContract;
    address private seedAddress;
    IATDeployer private deployerAT;
    address private ATDAddress;
    ITDeployer private deployerT;
    address private TDAddress;
    IFPDeployer private deployerFP;
    address private FPDAddress;

    address private internalDEXAddress;

    uint private factoryDeployBlock;

    event NewPanelCreated(address, address, address, address, uint);
    event ATFactoryAddressChanged();
    event TFactoryAddressChanged();
    event FPFactoryAddressChanged();
    event InternalDEXAddressChanged();

    constructor (address _seedAddress, address _ATDAddress, address _TDAddress, address _FPDAddress) public {
        seedAddress = _seedAddress;
        seedContract = IERC20Seed(seedAddress);
        ATDAddress = _ATDAddress;
        deployerAT = IATDeployer(ATDAddress);
        TDAddress = _TDAddress;
        deployerT = ITDeployer(_TDAddress);
        FPDAddress = _FPDAddress;
        deployerFP = IFPDeployer(_FPDAddress);
        factoryDeployBlock = block.number;
    }

    /**
     * @dev change AdminTols deployer address
     * @param _newATD new AT deployer address
     */
    function changeATFactoryAddress(address _newATD) external onlyOwner {
        require(block.number < 8850000, "Time expired!");
        require(_newATD != address(0), "Address not suitable!");
        require(_newATD != ATDAddress, "AT factory address not changed!");
        ATDAddress = _newATD;
        deployerAT = IATDeployer(ATDAddress);
        emit ATFactoryAddressChanged();
    }

    /**
     * @dev change Token deployer address
     * @param _newTD new T deployer address
     */
    function changeTDeployerAddress(address _newTD) external onlyOwner {
        require(block.number < 8850000, "Time expired!");
        require(_newTD != address(0), "Address not suitable!");
        require(_newTD != TDAddress, "AT factory address not changed!");
        TDAddress = _newTD;
        deployerT = ITDeployer(TDAddress);
        emit TFactoryAddressChanged();
    }

    /**
     * @dev change Funding Panel deployer address
     * @param _newFPD new FP deployer address
     */
    function changeFPDeployerAddress(address _newFPD) external onlyOwner {
        require(block.number < 8850000, "Time expired!");
        require(_newFPD != address(0), "Address not suitable!");
        require(_newFPD != ATDAddress, "AT factory address not changed!");
        FPDAddress = _newFPD;
        deployerFP = IFPDeployer(FPDAddress);
        emit FPFactoryAddressChanged();
    }

    /**
     * @dev set internal DEX address
     * @param _dexAddress internal DEX address
     */
    function setInternalDEXAddress(address _dexAddress) external onlyOwner {
        require(block.number < 8850000, "Time expired!");
        require(_dexAddress != address(0), "Address not suitable!");
        require(_dexAddress != internalDEXAddress, "AT factory address not changed!");
        internalDEXAddress = _dexAddress;
        emit InternalDEXAddressChanged();
    }

    /**
     * @dev deploy a new set of contracts for the Panel, with all params needed by contracts. Set the minter address for Token contract,
     * Owner is set as a manager in WL, Funding and FundsUnlocker, DEX is whitelisted
     * @param _name name of the token to be deployed
     * @param _symbol symbol of the token to be deployed
     * @param _setDocURL URL of the document describing the Panel
     * @param _setDocHash hash of the document describing the Panel
     * @param _exchRateSeed exchange rate between SEED tokens received and tokens given to the SEED sender (multiply by 10^_exchRateDecim)
     * @param _exchRateOnTop exchange rate between SEED token received and tokens minted on top (multiply by 10^_exchRateDecim)
     * @param _seedMaxSupply max supply of SEED tokens accepted by this contract
     * @param _WLAnonymThr max anonym threshold
     */
    function deployPanelContracts(string memory _name, string memory _symbol, string memory _setDocURL, bytes32 _setDocHash,
                            uint256 _exchRateSeed, uint256 _exchRateOnTop, uint256 _seedMaxSupply, uint256 _WLAnonymThr) public {
        address sender = msg.sender;

        require(sender != address(0), "Sender Address is zero");
        require(internalDEXAddress != address(0), "Internal DEX Address is zero");

        deployers[sender] = true;
        deployerList.push(sender);
        deployerLength = deployerList.length;

        address newAT = deployerAT.newAdminTools(_WLAnonymThr);
        ATContracts[newAT] = true;
        ATContractsList.push(newAT);
        address newT = deployerT.newToken(sender, _name, _symbol, newAT);
        TContracts[newT] = true;
        TContractsList.push(newT);
        address newFP = deployerFP.newFundingPanel(sender, _setDocURL, _setDocHash, _exchRateSeed, _exchRateOnTop,
                                            seedAddress, _seedMaxSupply, newT, newAT, (deployerLength-1));
        FPContracts[newFP] = true;
        FPContractsList.push(newFP);

        IAdminTools ATBrandNew = IAdminTools(newAT);
        ATBrandNew.setFFPAddresses(address(this), newFP);
        ATBrandNew.setMinterAddress(newFP);
        ATBrandNew.addWLManagers(address(this));
        ATBrandNew.addWLManagers(sender);
        ATBrandNew.addFundingManagers(sender);
        ATBrandNew.addFundsUnlockerManagers(sender);
        ATBrandNew.setWalletOnTopAddress(sender);

        uint256 dexMaxAmnt = _exchRateSeed.mul(300000000);  //Seed total supply
        ATBrandNew.addToWhitelist(internalDEXAddress, dexMaxAmnt);

        uint256 onTopMaxAmnt = _seedMaxSupply.mul(_exchRateSeed).div(10**18);
        ATBrandNew.addToWhitelist(sender, onTopMaxAmnt);

        ATBrandNew.removeWLManagers(address(this));

        Ownable customOwnable = Ownable(newAT);
        customOwnable.transferOwnership(sender);

        emit NewPanelCreated(sender, newAT, newT, newFP, deployerLength);
    }

    /**
     * @dev get deployers number
     */
    function getTotalDeployer() external view returns(uint256) {
        return deployerList.length;
    }

    /**
     * @dev get AT contracts number
     */
    function getTotalATContracts() external view returns(uint256) {
        return ATContractsList.length;
    }

    /**
     * @dev get T contracts number
     */
    function getTotalTContracts() external view returns(uint256) {
        return TContractsList.length;
    }

    /**
     * @dev get FP contracts number
     */
    function getTotalFPContracts() external view returns(uint256) {
        return FPContractsList.length;
    }

    /**
     * @dev get if address is a deployer
     */
    function isFactoryDeployer(address _addr) external view returns(bool) {
        return deployers[_addr];
    }

    /**
     * @dev get if address is an AT contract generated by factory
     */
    function isFactoryATGenerated(address _addr) external view returns(bool) {
        return ATContracts[_addr];
    }

    /**
     * @dev get if address is a T contract generated by factory
     */
    function isFactoryTGenerated(address _addr) external view returns(bool) {
        return TContracts[_addr];
    }

    /**
     * @dev get if address is a T contract generated by factory
     */
    function isFactoryFPGenerated(address _addr) external view returns(bool) {
        return FPContracts[_addr];
    }

    /**
     * @dev get the i-th element in every array
     */
    function getContractsByIndex(uint256 _index) external view returns (address, address, address, address) {
        return(deployerList[_index], ATContractsList[_index], TContractsList[_index], FPContractsList[_index]);
    }

    /**
     * @dev get the i-th element in FPContractsList array
     */
    function getFPAddressByIndex(uint256 _index) external view returns (address) {
        return FPContractsList[_index];
    }

    /**
     * @dev get the i-th element in FPContractsList array
     */
    function getFactoryContext() external view returns (address, address, uint) {
        return (seedAddress, internalDEXAddress, factoryDeployBlock);
    }

}