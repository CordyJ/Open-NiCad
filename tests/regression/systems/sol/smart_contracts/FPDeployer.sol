/**
 *Submitted for verification at Etherscan.io on 2019-08-10
*/

/**
 * SEED Platform Generator FPDeployer
 */

pragma solidity ^0.5.2;


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


/**
 * @dev Interface of the ERC20 standard as defined in the EIP. Does not include
 * the optional functions; to access them see `ERC20Detailed`.
 */
interface IERC20 {
    /**
     * @dev Returns the amount of tokens in existence.
     */
    function totalSupply() external view returns (uint256);

    /**
     * @dev Returns the amount of tokens owned by `account`.
     */
    function balanceOf(address account) external view returns (uint256);

    /**
     * @dev Moves `amount` tokens from the caller's account to `recipient`.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a `Transfer` event.
     */
    function transfer(address recipient, uint256 amount) external returns (bool);

    /**
     * @dev Returns the remaining number of tokens that `spender` will be
     * allowed to spend on behalf of `owner` through `transferFrom`. This is
     * zero by default.
     *
     * This value changes when `approve` or `transferFrom` are called.
     */
    function allowance(address owner, address spender) external view returns (uint256);

    /**
     * @dev Sets `amount` as the allowance of `spender` over the caller's tokens.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * > Beware that changing an allowance with this method brings the risk
     * that someone may use both the old and the new allowance by unfortunate
     * transaction ordering. One possible solution to mitigate this race
     * condition is to first reduce the spender's allowance to 0 and set the
     * desired value afterwards:
     * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
     *
     * Emits an `Approval` event.
     */
    function approve(address spender, uint256 amount) external returns (bool);

    /**
     * @dev Moves `amount` tokens from `sender` to `recipient` using the
     * allowance mechanism. `amount` is then deducted from the caller's
     * allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a `Transfer` event.
     */
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

    /**
     * @dev Emitted when `value` tokens are moved from one account (`from`) to
     * another (`to`).
     *
     * Note that `value` may be zero.
     */
    event Transfer(address indexed from, address indexed to, uint256 value);

    /**
     * @dev Emitted when the allowance of a `spender` for an `owner` is set by
     * a call to `approve`. `value` is the new allowance.
     */
    event Approval(address indexed owner, address indexed spender, uint256 value);
}


/**
 * @dev Implementation of the `IERC20` interface.
 *
 * This implementation is agnostic to the way tokens are created. This means
 * that a supply mechanism has to be added in a derived contract using `_mint`.
 * For a generic mechanism see `ERC20Mintable`.
 *
 * *For a detailed writeup see our guide [How to implement supply
 * mechanisms](https://forum.zeppelin.solutions/t/how-to-implement-erc20-supply-mechanisms/226).*
 *
 * We have followed general OpenZeppelin guidelines: functions revert instead
 * of returning `false` on failure. This behavior is nonetheless conventional
 * and does not conflict with the expectations of ERC20 applications.
 *
 * Additionally, an `Approval` event is emitted on calls to `transferFrom`.
 * This allows applications to reconstruct the allowance for all accounts just
 * by listening to said events. Other implementations of the EIP may not emit
 * these events, as it isn't required by the specification.
 *
 * Finally, the non-standard `decreaseAllowance` and `increaseAllowance`
 * functions have been added to mitigate the well-known issues around setting
 * allowances. See `IERC20.approve`.
 */
contract ERC20 is IERC20 {
    using SafeMath for uint256;

    mapping (address => uint256) private _balances;

    mapping (address => mapping (address => uint256)) private _allowances;

    uint256 private _totalSupply;

    /**
     * @dev See `IERC20.totalSupply`.
     */
    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev See `IERC20.balanceOf`.
     */
    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    /**
     * @dev See `IERC20.transfer`.
     *
     * Requirements:
     *
     * - `recipient` cannot be the zero address.
     * - the caller must have a balance of at least `amount`.
     */
    function transfer(address recipient, uint256 amount) public returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }

    /**
     * @dev See `IERC20.allowance`.
     */
    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }

    /**
     * @dev See `IERC20.approve`.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
     */
    function approve(address spender, uint256 value) public returns (bool) {
        _approve(msg.sender, spender, value);
        return true;
    }

    /**
     * @dev See `IERC20.transferFrom`.
     *
     * Emits an `Approval` event indicating the updated allowance. This is not
     * required by the EIP. See the note at the beginning of `ERC20`;
     *
     * Requirements:
     * - `sender` and `recipient` cannot be the zero address.
     * - `sender` must have a balance of at least `value`.
     * - the caller must have allowance for `sender`'s tokens of at least
     * `amount`.
     */
    function transferFrom(address sender, address recipient, uint256 amount) public returns (bool) {
        _transfer(sender, recipient, amount);
        _approve(sender, msg.sender, _allowances[sender][msg.sender].sub(amount));
        return true;
    }

    /**
     * @dev Atomically increases the allowance granted to `spender` by the caller.
     *
     * This is an alternative to `approve` that can be used as a mitigation for
     * problems described in `IERC20.approve`.
     *
     * Emits an `Approval` event indicating the updated allowance.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
     */
    function increaseAllowance(address spender, uint256 addedValue) public returns (bool) {
        _approve(msg.sender, spender, _allowances[msg.sender][spender].add(addedValue));
        return true;
    }

    /**
     * @dev Atomically decreases the allowance granted to `spender` by the caller.
     *
     * This is an alternative to `approve` that can be used as a mitigation for
     * problems described in `IERC20.approve`.
     *
     * Emits an `Approval` event indicating the updated allowance.
     *
     * Requirements:
     *
     * - `spender` cannot be the zero address.
     * - `spender` must have allowance for the caller of at least
     * `subtractedValue`.
     */
    function decreaseAllowance(address spender, uint256 subtractedValue) public returns (bool) {
        _approve(msg.sender, spender, _allowances[msg.sender][spender].sub(subtractedValue));
        return true;
    }

    /**
     * @dev Moves tokens `amount` from `sender` to `recipient`.
     *
     * This is internal function is equivalent to `transfer`, and can be used to
     * e.g. implement automatic token fees, slashing mechanisms, etc.
     *
     * Emits a `Transfer` event.
     *
     * Requirements:
     *
     * - `sender` cannot be the zero address.
     * - `recipient` cannot be the zero address.
     * - `sender` must have a balance of at least `amount`.
     */
    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(sender != address(0), "ERC20: transfer from the zero address");
        require(recipient != address(0), "ERC20: transfer to the zero address");

        _balances[sender] = _balances[sender].sub(amount);
        _balances[recipient] = _balances[recipient].add(amount);
        emit Transfer(sender, recipient, amount);
    }

    /** @dev Creates `amount` tokens and assigns them to `account`, increasing
     * the total supply.
     *
     * Emits a `Transfer` event with `from` set to the zero address.
     *
     * Requirements
     *
     * - `to` cannot be the zero address.
     */
    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: mint to the zero address");

        _totalSupply = _totalSupply.add(amount);
        _balances[account] = _balances[account].add(amount);
        emit Transfer(address(0), account, amount);
    }

     /**
     * @dev Destoys `amount` tokens from `account`, reducing the
     * total supply.
     *
     * Emits a `Transfer` event with `to` set to the zero address.
     *
     * Requirements
     *
     * - `account` cannot be the zero address.
     * - `account` must have at least `amount` tokens.
     */
    function _burn(address account, uint256 value) internal {
        require(account != address(0), "ERC20: burn from the zero address");

        _totalSupply = _totalSupply.sub(value);
        _balances[account] = _balances[account].sub(value);
        emit Transfer(account, address(0), value);
    }

    /**
     * @dev Sets `amount` as the allowance of `spender` over the `owner`s tokens.
     *
     * This is internal function is equivalent to `approve`, and can be used to
     * e.g. set automatic allowances for certain subsystems, etc.
     *
     * Emits an `Approval` event.
     *
     * Requirements:
     *
     * - `owner` cannot be the zero address.
     * - `spender` cannot be the zero address.
     */
    function _approve(address owner, address spender, uint256 value) internal {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = value;
        emit Approval(owner, spender, value);
    }

    /**
     * @dev Destoys `amount` tokens from `account`.`amount` is then deducted
     * from the caller's allowance.
     *
     * See `_burn` and `_approve`.
     */
    function _burnFrom(address account, uint256 amount) internal {
        _burn(account, amount);
        _approve(account, msg.sender, _allowances[account][msg.sender].sub(amount));
    }
}


interface IToken {
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);
    function paused() external view returns (bool);
    function pause() external;
    function unpause() external;
    function isImportedContract(address) external view returns (bool);
    function getImportedContractRate(address) external view returns (uint256);
    function setImportedContract(address, uint256) external;
    function checkTransferAllowed (address, address, uint256) external view returns (byte);
    function checkTransferFromAllowed (address, address, uint256) external view returns (byte);
    function checkMintAllowed (address, uint256) external pure returns (byte);
    function checkBurnAllowed (address, uint256) external pure returns (byte);
}


contract Token is IToken, ERC20, Ownable {

    string private _name;
    string private _symbol;
    uint8 private _decimals;

    IAdminTools private ATContract;
    address private ATAddress;

    byte private constant STATUS_ALLOWED = 0x11;
    byte private constant STATUS_DISALLOWED = 0x10;

    bool private _paused;

    struct contractsFeatures {
        bool permission;
        uint256 tokenRateExchange;
    }

    mapping(address => contractsFeatures) private contractsToImport;

    event Paused(address account);
    event Unpaused(address account);

    constructor(string memory name, string memory symbol, address _ATAddress) public {
        _name = name;
        _symbol = symbol;
        _decimals = 18;
        ATAddress = _ATAddress;
        ATContract = IAdminTools(ATAddress);
        _paused = false;
    }

    modifier onlyMinterAddress() {
        require(ATContract.getMinterAddress() == msg.sender, "Address can not mint!");
        _;
    }

    /**
     * @dev Modifier to make a function callable only when the contract is not paused.
     */
    modifier whenNotPaused() {
        require(!_paused, "Token Contract paused...");
        _;
    }

    /**
     * @dev Modifier to make a function callable only when the contract is paused.
     */
    modifier whenPaused() {
        require(_paused, "Token Contract not paused");
        _;
    }

    /**
     * @return the name of the token.
     */
    function name() external view returns (string memory) {
        return _name;
    }

    /**
     * @return the symbol of the token.
     */
    function symbol() external view returns (string memory) {
        return _symbol;
    }

    /**
     * @return the number of decimals of the token.
     */
    function decimals() external view returns (uint8) {
        return _decimals;
    }

    /**
     * @return true if the contract is paused, false otherwise.
     */
    function paused() external view returns (bool) {
        return _paused;
    }

    /**
     * @dev called by the owner to pause, triggers stopped state
     */
    function pause() external onlyOwner whenNotPaused {
        _paused = true;
        emit Paused(msg.sender);
    }

    /**
     * @dev called by the owner to unpause, returns to normal state
     */
    function unpause() external onlyOwner whenPaused {
        _paused = false;
        emit Unpaused(msg.sender);
    }

    /**
     * @dev check if the contract can be imported to change with this token.
     * @param _contract address of token to be imported
     */
    function isImportedContract(address _contract) external view returns (bool) {
        return contractsToImport[_contract].permission;
    }

    /**
     * @dev get the exchange rate between token to be imported and this token.
     * @param _contract address of token to be exchange
     */
    function getImportedContractRate(address _contract) external view returns (uint256) {
        return contractsToImport[_contract].tokenRateExchange;
    }

    /**
     * @dev set the address of the token to be imported and its exchange rate.
     * @param _contract address of token to be imported
     * @param _exchRate exchange rate between token to be imported and this token.
     */
    function setImportedContract(address _contract, uint256 _exchRate) external onlyOwner {
        require(_contract != address(0), "Address not allowed!");
        require(_exchRate >= 0, "Rate exchange not allowed!");
        contractsToImport[_contract].permission = true;
        contractsToImport[_contract].tokenRateExchange = _exchRate;
    }

    function transfer(address _to, uint256 _value) public whenNotPaused returns (bool) {
        require(checkTransferAllowed(msg.sender, _to, _value) == STATUS_ALLOWED, "transfer must be allowed");
        return ERC20.transfer(_to, _value);
    }

    function transferFrom(address _from, address _to, uint256 _value) public whenNotPaused returns (bool) {
        require(checkTransferFromAllowed(_from, _to, _value) == STATUS_ALLOWED, "transfer must be allowed");
        return ERC20.transferFrom(_from, _to,_value);
    }

    function mint(address _account, uint256 _amount) public whenNotPaused onlyMinterAddress {
        require(checkMintAllowed(_account, _amount) == STATUS_ALLOWED, "mint must be allowed");
        ERC20._mint(_account, _amount);
    }

    function burn(address _account, uint256 _amount) public whenNotPaused onlyMinterAddress {
        require(checkBurnAllowed(_account, _amount) == STATUS_ALLOWED, "burn must be allowed");
        ERC20._burn(_account, _amount);
    }

    /**
     * @dev check if the SEED sender address could receive new tokens.
     * @param _holder address of the SEED sender
     * @param _amountToAdd amount of tokens to be added to sender balance.
     */
    function okToTransferTokens(address _holder, uint256 _amountToAdd) public view returns (bool){
        uint256 holderBalanceToBe = balanceOf(_holder).add(_amountToAdd);
        bool okToTransfer = ATContract.isWhitelisted(_holder) && holderBalanceToBe <= ATContract.getMaxWLAmount(_holder) ? true :
                          holderBalanceToBe <= ATContract.getWLThresholdBalance() ? true : false;
        return okToTransfer;
    }

    function checkTransferAllowed (address _sender, address _receiver, uint256 _amount) public view returns (byte) {
        require(_sender != address(0), "Sender can not be 0!");
        require(_receiver != address(0), "Receiver can not be 0!");
        require(balanceOf(_sender) >= _amount, "Sender does not have enough tokens!");
        require(okToTransferTokens(_receiver, _amount), "Receiver not allowed to perform transfer!");
        return STATUS_ALLOWED;
    }

    function checkTransferFromAllowed (address _sender, address _receiver, uint256 _amount) public view returns (byte) {
        require(_sender != address(0), "Sender can not be 0!");
        require(_receiver != address(0), "Receiver can not be 0!");
        require(balanceOf(_sender) >= _amount, "Sender does not have enough tokens!");
        require(okToTransferTokens(_receiver, _amount), "Receiver not allowed to perform transfer!");
        return STATUS_ALLOWED;
    }

    function checkMintAllowed (address, uint256) public pure returns (byte) {
        //require(ATContract.isOperator(_minter), "Not Minter!");
        return STATUS_ALLOWED;
    }

    function checkBurnAllowed (address, uint256) public pure returns (byte) {
        // default
        return STATUS_ALLOWED;
    }

}


interface IFundingPanel {
    function getFactoryDeployIndex() external view returns(uint);
    function isMemberInserted(address) external view returns(bool);
    function addMemberToSet(address, uint8, string calldata, bytes32) external returns (bool);
    function enableMember(address) external;
    function disableMemberByStaffRetire(address) external;
    function disableMemberByStaffForExit(address) external;
    function disableMemberByMember(address) external;
    function changeMemberData(address, string calldata, bytes32) external;
    function changeTokenExchangeRate(uint256) external;
    function changeTokenExchangeOnTopRate(uint256) external;
    function getOwnerData() external view returns (string memory, bytes32);
    function setOwnerData(string calldata, bytes32) external;
    function getMembersNumber() external view returns (uint);
    function getMemberAddressByIndex(uint8) external view returns (address);
    function getMemberDataByAddress(address _memberWallet) external view returns (bool, uint8, string memory, bytes32, uint256, uint, uint256);
    function setNewSeedMaxSupply(uint256) external returns (uint256);
    function holderSendSeeds(uint256) external;
    function unlockFunds(address, uint256) external;
    function burnTokensForMember(address, uint256) external;
    function importOtherTokens(address, uint256) external;
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


contract FundingPanel is Ownable, IFundingPanel {
    using SafeMath for uint256;

    // address private owner;
    string private setDocURL;
    bytes32 private setDocHash;

    address public seedAddress;
    IERC20Seed private seedToken;
    Token private token;
    address public tokenAddress;
    IAdminTools private ATContract;
    address public ATAddress;

    uint8 public exchRateDecimals;
    uint256 public exchangeRateOnTop;
    uint256 public exchangeRateSeed;

    uint public factoryDeployIndex;

    uint256 public seedMaxSupply;
    uint256 public totalSentSeed;

    struct infoMember {
        bool isInserted;
        uint8 disabled; //0=enabled, 1=exit, 2=SetOwnerDisabled, 3=memberDisabled
        string memberURL;
        bytes32 memberHash;
        uint256 burnedTokens;
        uint listPointer;
        uint256 memberUnlockedSeeds;
    }
    mapping(address => infoMember) public membersArray; // mapping of members
    address[] public membersList; //array for counting or accessing in a sequencialing way the members

    event MemberAdded();
    //event MemberRemoved();
    event MemberEnabled(uint pointer);
    event MemberDisabled(uint pointer);
    event MemberDisabledByMember(uint pointer);
    event MemberDataChanged(uint pointer);
    event TokenExchangeRateChanged();
    event TokenExchangeOnTopRateChanged();
    event TokenExchangeDecimalsChanged();
    event OwnerDataChanged();
    event NewSeedMaxSupplyChanged();
    event MintedToken(uint256 amount, uint256 amountOnTop);
    event FundsUnlocked();
    event TokensBurnedForMember(uint pointer);
    event MintedImportedToken(uint256 newTokenAmount);

    constructor (string memory _setDocURL, bytes32 _setDocHash, uint256 _exchRateSeed, uint256 _exchRateOnTop,
                address _seedTokenAddress, uint256 _seedMaxSupply, address _tokenAddress, address _ATAddress, uint _deployIndex) public {
        setDocURL = _setDocURL;
        setDocHash = _setDocHash;

        exchangeRateSeed = _exchRateSeed;
        exchangeRateOnTop = _exchRateOnTop;
        exchRateDecimals = 18;

        factoryDeployIndex = _deployIndex;

        seedMaxSupply = _seedMaxSupply;

        tokenAddress = _tokenAddress;
        ATAddress = _ATAddress;
        seedAddress = _seedTokenAddress;
        seedToken = IERC20Seed(seedAddress);
        token = Token(tokenAddress);
        ATContract = IAdminTools(ATAddress);
    }


/**************** Modifiers ***********/

    modifier onlyMemberEnabled() {
        require(membersArray[msg.sender].isInserted && membersArray[msg.sender].disabled==0, "Member not present or not enabled");
        _;
    }

    modifier whitelistedOnly(address holder) {
        require(ATContract.isWhitelisted(holder), "Investor is not whitelisted!");
        _;
    }

    modifier holderEnabledInSeeds(address _holder, uint256 _seedAmountToAdd) {
        uint256 amountInTokens = getTokenExchangeAmount(_seedAmountToAdd);
        uint256 holderBalanceToBe = token.balanceOf(_holder).add(amountInTokens);
        bool okToInvest = ATContract.isWhitelisted(_holder) && holderBalanceToBe <= ATContract.getMaxWLAmount(_holder) ? true :
                          holderBalanceToBe <= ATContract.getWLThresholdBalance() ? true : false;
        require(okToInvest, "Investor not allowed to perform operations!");
        _;
    }

    modifier onlyFundingOperators() {
        require(ATContract.isFundingOperator(msg.sender), "Not an authorized operator!");
        _;
    }

    modifier onlyFundsUnlockerOperators() {
        require(ATContract.isFundsUnlockerOperator(msg.sender), "Not an authorized operator!");
        _;
    }

    /**
     * @dev get Factory Deploy Index
     * @return uint index
     */
    function getFactoryDeployIndex() public view returns(uint) {
        return factoryDeployIndex;
    }

    /**
     * @dev find if a member is inserted
     * @return bool for success
     */
    function isMemberInserted(address memberWallet) public view returns(bool) {
        return membersArray[memberWallet].isInserted;
    }

    /**
     * @dev only operator members can add a member
     * @return bool for success
     */
    function addMemberToSet(address memberWallet, uint8 disabled, string calldata memberURL,
                            bytes32 memberHash) external onlyFundingOperators returns (bool) {
        require(!isMemberInserted(memberWallet), "Member already inserted!");
        uint memberPlace = membersList.push(memberWallet) - 1;
        infoMember memory tmpStUp = infoMember(true, disabled, memberURL, memberHash, 0, memberPlace, 0);
        membersArray[memberWallet] = tmpStUp;
        emit MemberAdded();
        return true;
    }

    /**
     * @dev only operator members can delete a member
     * @return bool for success
     */
/*    function deleteMemberFromSet(address memberWallet) public onlyFundingOperators returns (bool) {
        require(isMemberInserted(memberWallet), "Member to delete not found!");
        membersArray[memberWallet].isInserted = false;
        uint rowToDelete = membersArray[memberWallet].listPointer;
        address keyToMove = membersList[membersList.length-1];
        membersList[rowToDelete] = keyToMove;
        membersArray[keyToMove].listPointer = rowToDelete;
        membersList.length--;
        emit MemberRemoved();
        return true;
    }*/

    /**
     * @return get the number of inserted members in the set
     */
    function getMembersNumber() external view returns (uint) {
        return membersList.length;
    }

    /**
     * @dev only operator memebers can enable a member
     */
    function enableMember(address _memberAddress) external onlyFundingOperators {
        require(membersArray[_memberAddress].isInserted, "Member not present");
        membersArray[_memberAddress].disabled = 0;
        emit MemberEnabled(membersArray[_memberAddress].listPointer);
    }

    /**
     * @dev operator members can disable an already inserted member
     */
    function disableMemberByStaffRetire(address _memberAddress) external onlyFundingOperators {
        require(membersArray[_memberAddress].isInserted, "Member not present");
        membersArray[_memberAddress].disabled = 2;
        emit MemberDisabled(membersArray[_memberAddress].listPointer);
    }

    /**
     * @dev operator members can disable an already inserted member
     */
    function disableMemberByStaffForExit(address _memberAddress) external onlyFundingOperators {
        require(membersArray[_memberAddress].isInserted, "Member not present");
        membersArray[_memberAddress].disabled = 1;
        emit MemberDisabled(membersArray[_memberAddress].listPointer);
    }

    /**
     * @dev member can disable itself if already inserted and enabled
     */
    function disableMemberByMember(address _memberAddress) external onlyMemberEnabled {
        membersArray[_memberAddress].disabled = 3;
        emit MemberDisabledByMember(membersArray[_memberAddress].listPointer);
    }

    /**
     * @dev operator members can change URL and hash of an already inserted member
     */
    function changeMemberData(address _memberAddress, string calldata newURL, bytes32 newHash) external onlyFundingOperators {
        require(membersArray[_memberAddress].isInserted, "Member not present");
        membersArray[_memberAddress].memberURL = newURL;
        membersArray[_memberAddress].memberHash = newHash;
        emit MemberDataChanged(membersArray[_memberAddress].listPointer);
    }

    /**
     * @dev operator members can change the rate exchange of the set
     */
    function changeTokenExchangeRate(uint256 newExchRate) external onlyFundingOperators {
        require(newExchRate > 0, "Wrong exchange rate!");
        exchangeRateSeed = newExchRate;
        emit TokenExchangeRateChanged();
    }

    /**
     * @dev operator members can change the rate exchange on top of the set
     */
    function changeTokenExchangeOnTopRate(uint256 newExchRate) external onlyFundingOperators {
        require(newExchRate > 0, "Wrong exchange rate on top!");
        exchangeRateOnTop = newExchRate;
        emit TokenExchangeOnTopRateChanged();
    }


    /**
     * @dev Shows the amount of tokens the user will receive for amount of Seed token
     * @param _Amount Exchanged seed tokens amount to convert
     * @return The amount of token that will be received
     */
    function getTokenExchangeAmount(uint256 _Amount) internal view returns(uint256) {
        require(_Amount > 0, "Amount must be greater than 0!");
        return _Amount.mul(exchangeRateSeed).div(10 ** uint256(exchRateDecimals));
    }

    /**
     * @dev Shows the amount of token the owner will receive for amount of Seed token
     * @param _Amount Exchanged chong amount to convert
     * @return The amount of set Token that will be received
     */
    function getTokenExchangeAmountOnTop(uint256 _Amount) internal view returns(uint256) {
        require(_Amount > 0, "Amount must be greater than 0!");
        return _Amount.mul(exchangeRateOnTop).div(10 ** uint256(exchRateDecimals));
    }

    /**
     * @return get the set token address
     */
    function getTokenAddress() external view returns (address) {
        return tokenAddress;
    }

    /**
     * @return get the operator members URL and hash
     */
    function getOwnerData() external view returns (string memory, bytes32) {
        return (setDocURL, setDocHash);
    }

    /**
     * @dev set the owner URL and hash
     */
    function setOwnerData(string calldata _dataURL, bytes32 _dataHash) external onlyOwner {
        setDocURL = _dataURL;
        setDocHash = _dataHash;
        emit OwnerDataChanged();
    }

    /**
     * @return get the operator members URL and hash
     */
    function getMemberAddressByIndex(uint8 _index) external view returns (address) {
        return membersList[_index];
    }

    function getMemberDataByAddress(address _memberWallet) external view returns (bool, uint8, string memory, bytes32, uint256, uint, uint256) {
        require(membersArray[_memberWallet].isInserted, "Member not inserted");
        return(membersArray[_memberWallet].isInserted, membersArray[_memberWallet].disabled, membersArray[_memberWallet].memberURL,
                membersArray[_memberWallet].memberHash, membersArray[_memberWallet].burnedTokens,
                membersArray[_memberWallet].listPointer, membersArray[_memberWallet].memberUnlockedSeeds);
    }

    /**
     * @dev change the max Supply of SEED
     */
    function setNewSeedMaxSupply(uint256 _newMaxSeedSupply) external onlyFundingOperators returns (uint256) {
        seedMaxSupply = _newMaxSeedSupply;
        emit NewSeedMaxSupplyChanged();
        return seedMaxSupply;
    }

    /**
     * @dev get the number of Seed token inside the contract an mint new tokens forthe holders and the wallet "On Top"
     * @notice msg.sender has to approve transfer the seed tokens BEFORE calling this function
     */
    function holderSendSeeds(uint256 _seeds) external holderEnabledInSeeds(msg.sender, _seeds) {
        require(seedToken.balanceOf(address(this)).add(_seeds) <= seedMaxSupply, "Maximum supply reached!");
        require(seedToken.balanceOf(msg.sender) >= _seeds, "Not enough seeds in holder wallet");
        address walletOnTop = ATContract.getWalletOnTopAddress();
        require(ATContract.isWhitelisted(walletOnTop), "Owner wallet not whitelisted");
        seedToken.transferFrom(msg.sender, address(this), _seeds);
        totalSentSeed = totalSentSeed.add(_seeds);

        //apply conversion seed/set token
        uint256 amount = getTokenExchangeAmount(_seeds);
        token.mint(msg.sender, amount);

        uint256 amountOnTop = getTokenExchangeAmountOnTop(_seeds);
        if (amountOnTop > 0)
            token.mint(walletOnTop, amountOnTop);
        emit MintedToken(amount, amountOnTop);
    }

    /**
     * @dev Funds unlock by operator members
     */
    function unlockFunds(address memberWallet, uint256 amount) external onlyFundsUnlockerOperators {
         require(seedToken.balanceOf(address(this)) >= amount, "Not enough seeds to unlock!");
         require(membersArray[memberWallet].isInserted && membersArray[memberWallet].disabled==0, "Member not present or not enabled");
         seedToken.transfer(memberWallet, amount);
         membersArray[memberWallet].memberUnlockedSeeds = membersArray[memberWallet].memberUnlockedSeeds.add(amount);
         emit FundsUnlocked();
    }

    /**
     * @dev Burn tokens for members
     */
    function burnTokensForMember(address memberWallet, uint256 amount) external {
         require(token.balanceOf(msg.sender) >= amount, "Not enough tokens to burn!");
         require(membersArray[memberWallet].isInserted && membersArray[memberWallet].disabled==0, "Member not present or not enabled");
         membersArray[memberWallet].burnedTokens = membersArray[memberWallet].burnedTokens.add(amount);
         token.burn(msg.sender, amount);
         emit TokensBurnedForMember(membersArray[memberWallet].listPointer);
    }

    /**
     * @dev Import old tokens and mints the amount of this new token
     * @param _tokenAddress Token address to convert in this tokens
     * @param _tokenAmount Amount of old tokens to convert
     */
    function importOtherTokens(address _tokenAddress, uint256 _tokenAmount) external onlyOwner {
        require(token.isImportedContract(_tokenAddress), "Address not allowed!");
        require(token.getImportedContractRate(_tokenAddress) >= 0, "Rate exchange not allowed!");
        require(ATContract.isWhitelisted(msg.sender), "Wallet not whitelisted");
        uint256 newTokenAmount = _tokenAmount.mul(token.getImportedContractRate(_tokenAddress));
        uint256 holderBalanceToBe = token.balanceOf(msg.sender).add(newTokenAmount);
        bool okToInvest = ATContract.isWhitelisted(msg.sender) && holderBalanceToBe <= ATContract.getMaxWLAmount(msg.sender) ? true :
                          holderBalanceToBe <= ATContract.getWLThresholdBalance() ? true : false;
        require(okToInvest, "Wallet Threshold too low");
        token.mint(msg.sender, newTokenAmount);
        emit MintedImportedToken(newTokenAmount);
    }
}


interface IFPDeployer {
    function newFundingPanel(address, string calldata, bytes32, uint256, uint256,
                            address, uint256, address, address, uint) external returns(address);
    function setFactoryAddress(address) external;
    function getFactoryAddress() external view returns(address);
}


contract FPDeployer is Ownable, IFPDeployer {
    address private fAddress;

    event FundingPanelDeployed(uint deployedBlock);

    //constructor() public {}

    modifier onlyFactory() {
        require(msg.sender == fAddress, "Address not allowed to create FP!");
        _;
    }

    /**
     * @dev Set the factory address for deployment.
     * @param _fAddress The factory address.
     */
    function setFactoryAddress(address _fAddress) external onlyOwner {
        require(block.number < 8850000, "Time expired!");
        require(_fAddress != address(0), "Address not allowed");
        fAddress = _fAddress;
    }

    /**
     * @dev Get the factory address for deployment.
     */
    function getFactoryAddress() external view returns(address) {
        return fAddress;
    }

    /**
     * @dev deployment of a new Funding Panel contract
     * @param _caller address that will take the ownership of the contract
     * @param _setDocURL URL of the document describing the Panel
     * @param _setDocHash hash of the document describing the Panel
     * @param _exchRateSeed exchange rate between SEED tokens received and tokens given to the SEED sender (multiply by 10^_exchRateDecim)
     * @param _exchRateOnTop exchange rate between SEED token received and tokens minted on top (multiply by 10^_exchRateDecim)
     * @param _seedTokenAddress address of SEED token contract
     * @param _seedMaxSupply max supply of SEED tokens accepted by this contract
     * @param _tokenAddress address of the corresponding Token contract
     * @param _ATAddress address of the corresponding AdminTools contract
     * @param newLength number of this contract in the corresponding array in the Factory contract
     * @return address of the deployed Token contract
     */
    function newFundingPanel(address _caller, string calldata _setDocURL, bytes32 _setDocHash, uint256 _exchRateSeed, uint256 _exchRateOnTop,
                address _seedTokenAddress, uint256 _seedMaxSupply, address _tokenAddress, address _ATAddress, uint newLength) external onlyFactory returns(address) {
        require(_caller != address(0), "Sender Address is zero");
        FundingPanel c = new FundingPanel(_setDocURL, _setDocHash, _exchRateSeed, _exchRateOnTop,
                                              _seedTokenAddress, _seedMaxSupply, _tokenAddress, _ATAddress, newLength);
        c.transferOwnership(_caller);
        emit FundingPanelDeployed (block.number);
        return address(c);
    }

}