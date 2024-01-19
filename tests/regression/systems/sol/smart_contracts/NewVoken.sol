/**
 *Submitted for verification at Etherscan.io on 2019-08-11
*/

pragma solidity ^0.5.10;

// New Vision.Network 100G Token
//
// Upgraded in Aug 2019
//
// More info:
//   https://vision.network
//   https://voken.io
//
// Contact us:
//   [email protected]
//   [email protected]


/**
 * @dev Wrappers over Solidity's arithmetic operations with added overflow checks.
 */
library SafeMath256 {
    /**
     * @dev Returns the addition of two unsigned integers, reverting on overflow.
     */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "SafeMath: addition overflow");

        return c;
    }

    /**
     * @dev Returns the subtraction of two unsigned integers, reverting on
     * overflow (when the result is negative).
     */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        return sub(a, b, "SafeMath: subtraction overflow");
    }

    /**
     * @dev Returns the subtraction of two unsigned integers, reverting with custom message on
     * overflow (when the result is negative).
     */
    function sub(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
        require(b <= a, errorMessage);
        uint256 c = a - b;

        return c;
    }

    /**
     * @dev Returns the multiplication of two unsigned integers, reverting on overflow.
     */
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
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
     */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        return div(a, b, "SafeMath: division by zero");
    }

    /**
     * @dev Returns the integer division of two unsigned integers. Reverts with custom message on
     * division by zero. The result is rounded towards zero.
     */
    function div(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
        // Solidity only automatically asserts when dividing by 0
        require(b > 0, errorMessage);
        return a / b;
    }

    /**
     * @dev Returns the remainder of dividing two unsigned integers. (unsigned integer modulo),
     * Reverts when dividing by zero.
     */
    function mod(uint256 a, uint256 b) internal pure returns (uint256) {
        return mod(a, b, "SafeMath: modulo by zero");
    }

    /**
     * @dev Returns the remainder of dividing two unsigned integers. (unsigned integer modulo),
     * Reverts with custom message when dividing by zero.
     */
    function mod(uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256) {
        require(b != 0, errorMessage);
        return a % b;
    }
}


/**
 * @dev Library for managing addresses assigned to a Role.
 */
library Roles {
    struct Role {
        mapping (address => bool) bearer;
    }

    /**
     * @dev Give an account access to this role.
     */
    function add(Role storage role, address account) internal {
        require(!has(role, account), "Roles: account already has role");
        role.bearer[account] = true;
    }

    /**
     * @dev Remove an account's access to this role.
     */
    function remove(Role storage role, address account) internal {
        require(has(role, account), "Roles: account does not have role");
        role.bearer[account] = false;
    }

    /**
     * @dev Check if an account has this role.
     *
     * @return bool
     */
    function has(Role storage role, address account) internal view returns (bool) {
        require(account != address(0), "Roles: account is the zero address");
        return role.bearer[account];
    }
}


/**
 * @dev Interface of the ERC20 standard
 */
interface IERC20 {
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);

    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}


/**
 * @dev Interface of an allocation contract.
 */
interface IAllocation {
    function reservedOf(address account) external view returns (uint256);
}


/**
 * @dev Contract module which provides a basic access control mechanism, where
 * there is an account (an owner) that can be granted exclusive access to
 * specific functions.
 */
contract Ownable {
    address internal _owner;
    address internal _newOwner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event OwnershipAccepted(address indexed previousOwner, address indexed newOwner);


    /**
     * @dev Initializes the contract setting the deployer as the initial owner.
     */
    constructor () internal {
        _owner = msg.sender;
        emit OwnershipTransferred(address(0), _owner);
    }

    /**
     * @dev Returns the addresses of the current and new owner.
     */
    function owner() public view returns (address currentOwner, address newOwner) {
        currentOwner = _owner;
        newOwner = _newOwner;
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier onlyOwner() {
        require(isOwner(), "Ownable: caller is not the owner");
        _;
    }

    /**
     * @dev Returns true if the caller is the current owner.
     */
    function isOwner() public view returns (bool) {
        return msg.sender == _owner;
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     *
     * IMPORTANT: Need to run {acceptOwnership} by the new owner.
     */
    function _transferOwnership(address newOwner) internal {
        require(newOwner != address(0), "Ownable: new owner is the zero address");

        emit OwnershipTransferred(_owner, newOwner);
        _newOwner = newOwner;
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     *
     * Can only be called by the current owner.
     */
    function transferOwnership(address newOwner) public onlyOwner {
        _transferOwnership(newOwner);
    }

    /**
     * @dev Accept ownership of the contract.
     *
     * Can only be called by the new owner.
     */
    function acceptOwnership() public {
        require(msg.sender == _newOwner, "Ownable: caller is not the new owner address");
        require(msg.sender != address(0), "Ownable: caller is the zero address");

        emit OwnershipAccepted(_owner, msg.sender);
        _owner = msg.sender;
        _newOwner = address(0);
    }

    /**
     * @dev Rescue compatible ERC20 Token
     *
     * Can only be called by the current owner.
     */
    function rescueTokens(address tokenAddr, address recipient, uint256 amount) external onlyOwner {
        IERC20 _token = IERC20(tokenAddr);
        require(recipient != address(0), "Rescue: recipient is the zero address");
        uint256 balance = _token.balanceOf(address(this));

        require(balance >= amount, "Rescue: amount exceeds balance");
        _token.transfer(recipient, amount);
    }

    /**
     * @dev Withdraw Ether
     *
     * Can only be called by the current owner.
     */
    function withdrawEther(address payable recipient, uint256 amount) external onlyOwner {
        require(recipient != address(0), "Withdraw: recipient is the zero address");

        uint256 balance = address(this).balance;

        require(balance >= amount, "Withdraw: amount exceeds balance");
        recipient.transfer(amount);
    }
}


/**
 * @dev Base contract which allows children to implement an emergency stop mechanism.
 */
contract Pausable is Ownable {
    bool private _paused;

    event Paused(address account);
    event Unpaused(address account);


    /**
     * @dev Constructor
     */
    constructor () internal {
        _paused = false;
    }

    /**
     * @return Returns true if the contract is paused, false otherwise.
     */
    function paused() public view returns (bool) {
        return _paused;
    }

    /**
     * @dev Modifier to make a function callable only when the contract is not paused.
     */
    modifier whenNotPaused() {
        require(!_paused, "Paused");
        _;
    }

    /**
     * @dev Sets paused state.
     *
     * Can only be called by the current owner.
     */
    function setPaused(bool value) external onlyOwner {
        _paused = value;

        if (_paused) {
            emit Paused(msg.sender);
        } else {
            emit Unpaused(msg.sender);
        }
    }
}


/**
 * @title New Voken Main Contract
 */
contract NewVoken is Ownable, Pausable, IERC20 {
    using SafeMath256 for uint256;
    using Roles for Roles.Role;

    string private _name = "New Vision.Network 100G Token";
    string private _symbol = "VokenNEW";
    uint8 private _decimals = 6;
    uint256 private _cap;
    uint256 private _totalSupply;

    bool private _safeMode;
    bool private _whitelistingMode;
    uint256 private _whitelistCounter;
    uint256 private _whitelistTrigger = 1001000000;     // 1001 VOKEN for sign-up trigger
    uint256 private _whitelistRefund = 1000000;         //    1 VOKEN for success signal
    uint256 private _whitelistRewards = 1000000000;     // 1000 VOKEN for rewards
    uint256[15] private _whitelistRewardsArr = [
        300000000,  // 300 Voken for Level.1
        200000000,  // 200 Voken for Level.2
        100000000,  // 100 Voken for Level.3
        100000000,  // 100 Voken for Level.4
        100000000,  // 100 Voken for Level.5
        50000000,   //  50 Voken for Level.6
        40000000,   //  40 Voken for Level.7
        30000000,   //  30 Voken for Level.8
        20000000,   //  20 Voken for Level.9
        10000000,   //  10 Voken for Level.10
        10000000,   //  10 Voken for Level.11
        10000000,   //  10 Voken for Level.12
        10000000,   //  10 Voken for Level.13
        10000000,   //  10 Voken for Level.14
        10000000    //  10 Voken for Level.15
    ];

    Roles.Role private _globals;
    Roles.Role private _proxies;
    Roles.Role private _minters;

    mapping (address => uint256) private _balances;
    mapping (address => mapping (address => uint256)) private _allowances;
    mapping (address => IAllocation[]) private _allocations;
    mapping (address => mapping (address => bool)) private _addressAllocations;

    mapping (address => address) private _referee;
    mapping (address => address[]) private _referrals;

    event Donate(address indexed account, uint256 amount);
    event Burn(address indexed account, uint256 amount);
    event ProxyAdded(address indexed account);
    event ProxyRemoved(address indexed account);
    event GlobalAdded(address indexed account);
    event GlobalRemoved(address indexed account);
    event MinterAdded(address indexed account);
    event MinterRemoved(address indexed account);
    event Mint(address indexed account, uint256 amount);
    event MintWithAllocation(address indexed account, uint256 amount, IAllocation indexed allocationContract);
    event WhitelistSignUpEnabled();
    event WhitelistSignUpDisabled();
    event WhitelistSignUp(address indexed account, address indexed refereeAccount);


    /**
     * @dev Constructor
     */
    constructor () public {
        _cap = 35000000000000000;   // 35 billion cap, that is 35000000000.000000

        _whitelistingMode = true;
        _safeMode = true;

        _referee[msg.sender] = msg.sender;
        _whitelistCounter = 1;

        addGlobal(address(this));
        addProxy(msg.sender);
        addMinter(msg.sender);

        emit WhitelistSignUpEnabled();
        emit WhitelistSignUp(msg.sender, msg.sender);
    }

    /**
     * @dev Donate
     */
    function () external payable {
        if (msg.value > 0) {
            emit Donate(msg.sender, msg.value);
        }
    }

    /**
     * @dev Returns the full name of VOKEN.
     */
    function name() public view returns (string memory) {
        return _name;
    }

    /**
     * @dev Returns the symbol of VOKEN.
     */
    function symbol() public view returns (string memory) {
        return _symbol;
    }

    /**
     * @dev Returns the number of decimals used to get its user representation.
     */
    function decimals() public view returns (uint8) {
        return _decimals;
    }

    /**
     * @dev Returns the cap on VOKEN's total supply.
     */
    function cap() public view returns (uint256) {
        return _cap;
    }

    /**
     * @dev Returns the amount of VOKEN in existence.
     */
    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev Returns the amount of VOKEN owned by `account`.
     */
    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    /**
     * @dev Returns the reserved amount of VOKEN by `account`.
     */
    function reservedOf(address account) public view returns (uint256) {
        uint256 __reserved;

        uint256 __len = _allocations[account].length;
        if (__len > 0) {
            for (uint256 i = 0; i < __len; i++) {
                __reserved = __reserved.add(_allocations[account][i].reservedOf(account));
            }
        }

        return __reserved;
    }

    /**
     * @dev Returns the available amount of VOKEN by `account`.
     */
    function availableOf(address account) public view returns (uint256) {
        return balanceOf(account).sub(reservedOf(account));
    }

    /**
     * @dev Returns the available amount of VOKEN by `account` and a certain `amount`.
     */
    function _getAvailableAmount(address account, uint256 amount) internal view returns (uint256) {
        uint256 __available = balanceOf(account).sub(reservedOf(account));

        if (amount <= __available) {
            return amount;
        }

        else if (__available > 0) {
            return __available;
        }

        revert("VOKEN: available balance is zero");
    }

    /**
     * @dev Returns the allocation contracts' addresses on `account`.
     */
    function allocations(address account) public view returns (IAllocation[] memory contracts) {
        contracts = _allocations[account];
    }

    /**
     * @dev Moves `amount` VOKEN from the caller's account to `recipient`.
     *
     * Auto handle whitelist sign-up when `amount` is a specific value.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transfer(address recipient, uint256 amount) public whenNotPaused returns (bool) {
        // Whitelist sign-up
        if (amount == _whitelistTrigger && _whitelistingMode && whitelisted(recipient) && !whitelisted(msg.sender)) {
            _transfer(msg.sender, address(this), _whitelistTrigger);
            _whitelist(msg.sender, recipient);
            _distributeVokenForWhitelist(msg.sender);
        }

        // Burn
        else if (recipient == address(this) || recipient == address(0)) {
            _burn(msg.sender, amount);
        }

        // Normal Transfer
        else {
            _transfer(msg.sender, recipient, _getAvailableAmount(msg.sender, amount));
        }

        return true;
    }

    /**
     * @dev Moves `amount` VOKEN from `sender` to `recipient` using the
     * allowance mechanism. `amount` is then deducted from the caller's
     * allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     * Emits an {Approval} event indicating the updated allowance.
     */
    function transferFrom(address sender, address recipient, uint256 amount) public whenNotPaused returns (bool) {
        // Burn
        if (recipient == address(this) || recipient == address(0)) {
            _burn(msg.sender, amount);
        }

        // Normal transfer
        else {
            uint256 __amount = _getAvailableAmount(sender, amount);

            _transfer(sender, recipient, __amount);
            _approve(sender, msg.sender, _allowances[sender][msg.sender].sub(__amount, "VOKEN: transfer amount exceeds allowance"));
        }

        return true;
    }

    /**
     * @dev Destroys `amount` VOKEN from the caller.
     *
     * Emits a {Transfer} event with `to` set to the zero address.
     */
    function burn(uint256 amount) public whenNotPaused returns (bool) {
        _burn(msg.sender, amount);
        return true;
    }

    /**
     * @dev Destoys `amount` VOKEN from `account`.`amount` is then deducted
     * from the caller's allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     * Emits an {Approval} event indicating the updated allowance.
     */
    function burnFrom(address account, uint256 amount) public whenNotPaused returns (bool) {
        _burn(account, amount);
        _approve(account, msg.sender, _allowances[account][msg.sender].sub(amount, "VOKEN: burn amount exceeds allowance"));
        return true;
    }

    /**
     * @dev Creates `amount` VOKEN and assigns them to `account`.
     *
     * Can only be called by a minter.
     */
    function mint(address account, uint256 amount) public whenNotPaused onlyMinter returns (bool) {
        _mint(account, amount);
        return true;
    }

    /**
     * @dev Creates `amount` VOKEN and assigns them to `account`.
     *
     * With an `allocationContract`
     *
     * Can only be called by a minter.
     */
    function mintWithAllocation(address account, uint256 amount, IAllocation allocationContract) public whenNotPaused onlyMinter returns (bool) {
        _mintWithAllocation(account, amount, allocationContract);
        return true;
    }

    /**
     * @dev Sets `amount` as the allowance of `spender` over the caller's tokens.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits an {Approval} event.
     */
    function approve(address spender, uint256 value) public whenNotPaused returns (bool) {
        _approve(msg.sender, spender, value);
        return true;
    }

    /**
     * @dev Returns the remaining number of VOKEN that `spender` will be
     * allowed to spend on behalf of `owner` through {transferFrom}.
     * This is zero by default.
     */
    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }

    /**
     * @dev Atomically increases the allowance granted to `spender` by the caller.
     *
     * Emits an {Approval} event indicating the updated allowance.
     */
    function increaseAllowance(address spender, uint256 addedValue) public whenNotPaused returns (bool) {
        _approve(msg.sender, spender, _allowances[msg.sender][spender].add(addedValue));
        return true;
    }

    /**
     * @dev Atomically decreases the allowance granted to `spender` by the caller.
     *
     * Emits an {Approval} event indicating the updated allowance.
     */
    function decreaseAllowance(address spender, uint256 subtractedValue) public whenNotPaused returns (bool) {
        _approve(msg.sender, spender, _allowances[msg.sender][spender].sub(subtractedValue, "VOKEN: decreased allowance below zero"));
        return true;
    }

    /**
     * @dev Moves VOKEN `amount` from `sender` to `recipient`.
     *
     * May reject non-whitelist transaction.
     *
     * Emits a {Transfer} event.
     */
    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(recipient != address(0), "VOKEN: recipient is the zero address");

        if (_safeMode && !isGlobal(sender) && !isGlobal(recipient)) {
            require(whitelisted(sender), "VOKEN: sender is not whitelisted");
        }

        _balances[sender] = _balances[sender].sub(amount);
        _balances[recipient] = _balances[recipient].add(amount);
        emit Transfer(sender, recipient, amount);
    }

    /**
     * @dev Creates `amount` VOKEN and assigns them to `account`, increasing the total supply.
     *
     * Emits a {Mint} event.
     * Emits a {Transfer} event with `from` set to the zero address.
     */
    function _mint(address account, uint256 amount) internal {
        require(_totalSupply.add(amount) <= _cap, "VOKEN: total supply cap exceeded");
        require(account != address(0), "VOKEN: mint to the zero address");

        _totalSupply = _totalSupply.add(amount);
        _balances[account] = _balances[account].add(amount);
        emit Mint(account, amount);
        emit Transfer(address(0), account, amount);
    }

    /**
     * @dev Creates `amount` VOKEN and assigns them to `account`, increasing the total supply.
     *
     * With an `allocationContract`
     *
     * Emits a {Transfer} event with `from` set to the zero address.
     */
    function _mintWithAllocation(address account, uint256 amount, IAllocation allocationContract) internal {
        require(_totalSupply.add(amount) <= _cap, "VOKEN: total supply cap exceeded");
        require(account != address(0), "VOKEN: mint to the zero address");

        _totalSupply = _totalSupply.add(amount);
        _balances[account] = _balances[account].add(amount);

        if (!_addressAllocations[account][address(allocationContract)]) {
            _allocations[account].push(allocationContract);
            _addressAllocations[account][address(allocationContract)] = true;
        }

        emit MintWithAllocation(account, amount, allocationContract);
        emit Transfer(address(0), account, amount);
    }

    /**
     * @dev Destroys `amount` VOKEN from `account`, reducing the total supply.
     *
     * Emits a {Burn} event.
     * Emits a {Transfer} event with `to` set to the zero address.
     */
    function _burn(address account, uint256 amount) internal {
        uint256 __amount = _getAvailableAmount(account, amount);

        _balances[account] = _balances[account].sub(__amount, "VOKEN: burn amount exceeds balance");
        _totalSupply = _totalSupply.sub(__amount);
        _cap = _cap.sub(__amount);
        emit Burn(account, __amount);
        emit Transfer(account, address(0), __amount);
    }

    /**
     * @dev Sets `amount` as the allowance of `spender` over the `owner`s VOKEN.
     *
     * Emits an {Approval} event.
     */
    function _approve(address owner, address spender, uint256 value) internal {
        require(owner != address(0), "VOKEN: approve from the zero address");
        require(spender != address(0), "VOKEN: approve to the zero address");
        require(value <= _getAvailableAmount(spender, value), "VOKEN: approve exceeds available balance");

        _allowances[owner][spender] = value;
        emit Approval(owner, spender, value);
    }









    /**
     * @dev Sets the full name of VOKEN.
     *
     * Can only be called by the current owner.
     */
    function rename(string calldata value) external onlyOwner {
        _name = value;
    }

    /**
     * @dev Sets the symbol of VOKEN.
     *
     * Can only be called by the current owner.
     */
    function setSymbol(string calldata value) external onlyOwner {
        _symbol = value;
    }

    /**
     * @dev Returns true if the `account` is whitelisted.
     */
    function whitelisted(address account) public view returns (bool) {
        return _referee[account] != address(0);
    }

    /**
     * @dev Returns the whitelist counter.
     */
    function whitelistCounter() public view returns (uint256) {
        return _whitelistCounter;
    }

    /**
     * @dev Returns true if the sign-up for whitelist is allowed.
     */
    function whitelistingMode() public view returns (bool) {
        return _whitelistingMode;
    }

    /**
     * @dev Returns the referee of an `account`.
     */
    function whitelistReferee(address account) public view returns (address) {
        return _referee[account];
    }

    /**
     * @dev Returns referrals of a `account`
     */
    function whitelistReferrals(address account) public view returns (address[] memory) {
        return _referrals[account];
    }

    /**
     * @dev Returns the referrals count of an `account`.
     */
    function whitelistReferralsCount(address account) public view returns (uint256) {
        return _referrals[account].length;
    }

    /**
     * @dev Push whitelist, batch.
     *
     * Can only be called by a proxy.
     */
    function pushWhitelist(address[] memory accounts, address[] memory refereeAccounts) public onlyProxy returns (bool) {
        require(accounts.length == refereeAccounts.length, "VOKEN Whitelist: batch length is not match");

        for (uint256 i = 0; i < accounts.length; i++) {
            if (accounts[i] != address(0) && !whitelisted(accounts[i]) && whitelisted(refereeAccounts[i])) {
                _whitelist(accounts[i], refereeAccounts[i]);
            }
        }

        return true;
    }

    /**
     * @dev Whitelist an `account` with a `refereeAccount`.
     *
     * Emits {WhitelistSignUp} event.
     */
    function _whitelist(address account, address refereeAccount) internal {
        require(!whitelisted(account), "Whitelist: account is already whitelisted");
        require(whitelisted(refereeAccount), "Whitelist: refereeAccount is not whitelisted");

        _referee[account] = refereeAccount;
        _referrals[refereeAccount].push(account);
        _whitelistCounter = _whitelistCounter.add(1);

        emit WhitelistSignUp(account, refereeAccount);
    }

    /**
     * @dev Distribute VOKEN.
     */
    function _distributeVokenForWhitelist(address account) internal {
        uint256 __distributedAmount;
        uint256 __burnAmount;

        address __cursor = account;
        for(uint i = 0; i < _whitelistRewardsArr.length; i++) {
            address __receiver = _referee[__cursor];

            if (__receiver != address(0)) {
                if (__receiver != __cursor && _referrals[__receiver].length > i) {
                    _transfer(address(this), __receiver, _whitelistRewardsArr[i]);
                    __distributedAmount = __distributedAmount.add(_whitelistRewardsArr[i]);
                }
            }

            __cursor = _referee[__cursor];
        }

        // Burn
        __burnAmount = _whitelistRewards.sub(__distributedAmount);
        if (__burnAmount > 0) {
            _burn(address(this), __burnAmount);
        }

        // Transfer VOKEN refund as a success signal.
        _transfer(address(this), account, _whitelistRefund);
    }









    /**
     * @dev Enable/disable sign-up for whitelist.
     *
     * Can only be called by the current owner.
     */
    function setWhitelistingMode(bool value) public onlyOwner {
        _whitelistingMode = value;

        if (_whitelistingMode) {
            emit WhitelistSignUpEnabled();
        } else {
            emit WhitelistSignUpDisabled();
        }
    }

    /**
     * @dev Returns true if a transaction from non-whitelisted address is not allowed.
     */
    function safeMode() public view returns (bool) {
        return _safeMode;
    }

    /**
     * @dev Disable/enable non-whitelist transaction.
     *
     * Can only be called by the current owner.
     */
    function setSafeMode(bool value) public onlyOwner {
        _safeMode = value;
    }

    /**
     * @dev Returns true if the `account` has the Global role
     */
    function isGlobal(address account) public view returns (bool) {
        return _globals.has(account);
    }

    /**
     * @dev Give an `account` access to the Global role.
     *
     * Can only be called by the current owner.
     */
    function addGlobal(address account) public onlyOwner {
        _globals.add(account);
        emit GlobalAdded(account);
    }

    /**
     * @dev Remove an `account` access from the Global role.
     *
     * Can only be called by the current owner.
     */
    function removeGlobal(address account) public onlyOwner {
        _globals.remove(account);
        emit GlobalRemoved(account);
    }

    /**
     * @dev Throws if called by account which is not a proxy.
     */
    modifier onlyProxy() {
        require(isProxy(msg.sender), "ProxyRole: caller does not have the Proxy role");
        _;
    }

    /**
     * @dev Returns true if the `account` has the Proxy role.
     */
    function isProxy(address account) public view returns (bool) {
        return _proxies.has(account);
    }

    /**
     * @dev Give an `account` access to the Proxy role.
     *
     * Can only be called by the current owner.
     */
    function addProxy(address account) public onlyOwner {
        _proxies.add(account);
        emit ProxyAdded(account);
    }

    /**
     * @dev Remove an `account` access from the Proxy role.
     *
     * Can only be called by the current owner.
     */
    function removeProxy(address account) public onlyOwner {
        _proxies.remove(account);
        emit ProxyRemoved(account);
    }

    /**
     * @dev Throws if called by account which is not a minter.
     */
    modifier onlyMinter() {
        require(isMinter(msg.sender), "MinterRole: caller does not have the Minter role");
        _;
    }

    /**
     * @dev Returns true if the `account` has the Minter role
     */
    function isMinter(address account) public view returns (bool) {
        return _minters.has(account);
    }

    /**
     * @dev Give an `account` access to the Minter role.
     *
     * Can only be called by the current owner.
     */
    function addMinter(address account) public onlyOwner {
        _minters.add(account);
        emit MinterAdded(account);
    }

    /**
     * @dev Remove an `account` access from the Minter role.
     *
     * Can only be called by the current owner.
     */
    function removeMinter(address account) public onlyOwner {
        _minters.remove(account);
        emit MinterRemoved(account);
    }
}