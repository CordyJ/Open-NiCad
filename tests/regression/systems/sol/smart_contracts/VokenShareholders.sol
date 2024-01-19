/**
 *Submitted for verification at Etherscan.io on 2019-08-11
*/

pragma solidity ^0.5.10;

// Voken Shareholders Contract
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
 * @title Roles
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
     * @return bool
     */
    function has(Role storage role, address account) internal view returns (bool) {
        require(account != address(0), "Roles: account is the zero address");
        return role.bearer[account];
    }
}


/**
 * @dev Allocation for VOKEN
 */
library Allocations {
    using SafeMath256 for uint256;

    struct Allocation {
        uint256 amount;
    }

    /**
     * @dev Returns the available amount.
     */
    function available(Allocation storage self) internal view returns (uint256) {
        uint256 timestamp = 1588291199; // Thu, 30 Apr 2020 23:59:59 +0000
        uint256 interval = 1 days;
        uint256 steps = 61;

        if (now > timestamp) {
            if (interval == 0) {
                return self.amount;
            }

            uint256 __passed = now.sub(timestamp).div(interval).add(1);

            if (__passed >= steps) {
                return self.amount;
            }

            return self.amount.mul(__passed).div(steps);
        }

        return 0;
    }

    /**
     * @dev Returns the reserved amount.
     */
    function reserved(Allocation storage self) internal view returns (uint256) {
        return self.amount.sub(available(self));
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
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}


/**
 * @dev Interface of an allocation contract
 */
interface IAllocation {
    function reservedOf(address account) external view returns (uint256);
}


/**
 * @dev Interface of VOKEN
 */
interface IVoken {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function mintWithAllocation(address account, uint256 amount, address allocationContract) external returns (bool);
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
    function owner() public view returns (address, address) {
        return (_owner, _newOwner);
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
     * Need to run {acceptOwnership} by the new owner.
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

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     */
    function _transferOwnership(address newOwner) internal {
        require(newOwner != address(0), "Ownable: new owner is the zero address");

        emit OwnershipTransferred(_owner, newOwner);
        _newOwner = newOwner;
    }
}


/**
 * @title Voken Shareholders
 */
contract VokenShareholders is Ownable, IAllocation {
    using SafeMath256 for uint256;
    using Roles for Roles.Role;
    using Allocations for Allocations.Allocation;

    IVoken private _voken;
    Roles.Role private _proxies;

    uint256 private _page;
    uint256 private _ethers;
    uint256 private _vokens;

    address[] private _shareholders;
    mapping (address => bool) private _isShareholders;

    mapping (address => uint256) private _withdrawPos;
    mapping (uint256 => address[]) private _pageShareholders;
    mapping (uint256 => mapping (address => bool)) private _isPageShareholders;

    mapping (uint256 => uint256) private _pageEndingBlock;
    mapping (uint256 => uint256) private _pageEthers;
    mapping (uint256 => uint256) private _pageVokens;
    mapping (uint256 => uint256) private _pageVokenSum;
    mapping (uint256 => mapping (address => uint256)) private _pageVokenHoldings;
    mapping (uint256 => mapping (address => uint256)) private _pageEtherDividends;

    mapping (address => Allocations.Allocation[]) private _allocations;

    event Dividend(address indexed account, uint256 amount, uint256 page);
    event ProxyAdded(address indexed account);
    event ProxyRemoved(address indexed account);


    /**
     * @dev Constructor
     */
    constructor () public {
        _page = 1;

        addProxy(msg.sender);
    }

    /**
     * @dev Returns the max page number.
     */
    function page() public view returns (uint256) {
        return _page;
    }

    /**
     * @dev Returns the amount of deposited Ether.
     */
    function ethers() public view returns (uint256) {
        return _ethers;
    }

    /**
     * @dev Returns the amount of VOKEN holding by all shareholders.
     */
    function vokens() public view returns (uint256) {
        return _vokens;
    }

    /**
     * @dev Returns the shareholders counter on `pageNumber`.
     */
    function counter(uint256 pageNumber) public view returns (uint256) {
        if (pageNumber > 0) {
            return _pageShareholders[pageNumber].length;
        }

        return _shareholders.length;
    }

    /**
     * @dev Returns the shareholders list on `pageNumber`.
     */
    function shareholders(uint256 pageNumber) public view returns (address[] memory) {
        if (pageNumber > 0) {
            return _pageShareholders[pageNumber];
        }

        return _shareholders;
    }

    /**
     * @dev Returns the VOKEN main contract address.
     */
    function VOKEN() public view returns (IVoken) {
        return _voken;
    }

    /**
     * Returns the ending block number of `pageNumber`.
     */
    function pageEndingBlock(uint256 pageNumber) public view returns (uint256) {
        return _pageEndingBlock[pageNumber];
    }

    /**
     * @dev Returns the amount of deposited Ether at `pageNumber`.
     */
    function pageEthers(uint256 pageNumber) public view returns (uint256) {
        return _pageEthers[pageNumber];
    }

    /**
     * @dev Returns the amount of deposited Ether till `pageNumber`.
     */
    function pageEtherSum(uint256 pageNumber) public view returns (uint256) {
        uint256 __page = _pageNumber(pageNumber);
        uint256 __amount;

        for (uint256 i = 1; i <= __page; i++) {
            __amount = __amount.add(_pageEthers[i]);
        }

        return __amount;
    }

    /**
     * Returns the page number greater than 0 by `pageNmber`.
     */
    function _pageNumber(uint256 pageNumber) internal view returns (uint256) {
        if (pageNumber > 0) {
            return pageNumber;
        }

        else {
            return _page;
        }
    }

    /**
     * @dev Returns the amount of VOKEN holding by all shareholders at `pageNumber`.
     */
    function pageVokens(uint256 pageNumber) public view returns (uint256) {
        return _pageVokens[pageNumber];
    }

    /**
     * @dev Returns the amount of VOKEN holding by all shareholders till `pageNumber`.
     */
    function pageVokenSum(uint256 pageNumber) public view returns (uint256) {
        return _pageVokenSum[_pageNumber(pageNumber)];
    }

    /**
     * @dev Returns the amount of VOKEN holding by `account` and `pageNumber`.
     */
    function vokenHolding(address account, uint256 pageNumber) public view returns (uint256) {
        uint256 __page;
        uint256 __amount;

        if (pageNumber > 0) {
            __page = pageNumber;
        }

        else {
            __page = _page;
        }

        for (uint256 i = 1; i <= __page; i++) {
            __amount = __amount.add(_pageVokenHoldings[i][account]);
        }

        return __amount;
    }

    /**
     * @dev Returns the ether dividend of `account` on `pageNumber`.
     */
    function etherDividend(address account, uint256 pageNumber) public view returns (uint256 amount,
                                                                                     uint256 dividend,
                                                                                     uint256 remain) {
        if (pageNumber > 0) {
            amount = pageEthers(pageNumber).mul(vokenHolding(account, pageNumber)).div(pageVokenSum(pageNumber));
            dividend = _pageEtherDividends[pageNumber][account];
        }

        else {
            for (uint256 i = 1; i <= _page; i++) {
                uint256 __pageEtherDividend = pageEthers(i).mul(vokenHolding(account, i)).div(pageVokenSum(i));
                amount = amount.add(__pageEtherDividend);
                dividend = dividend.add(_pageEtherDividends[i][account]);
            }
        }

        remain = amount.sub(dividend);
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
     * @dev Returns the allocations counter on `account`.
     */
    function allocations(address account) public view returns (uint256 allocationsCounter) {
        allocationsCounter = _allocations[account].length;
    }

    /**
     * @dev Returns the allocation on `account` and an `index`.
     */
    function allocation(address account, uint256 index) public view returns (uint256 amount,
                                                                             uint256 timestamp,
                                                                             uint256 interval,
                                                                             uint256 steps,
                                                                             uint256 available,
                                                                             uint256 reserved) {
        if (index < _allocations[account].length) {
            amount = _allocations[account][index].amount;
            timestamp = 1588291199; // Thu, 30 Apr 2020 23:59:59 +0000
            interval = 1 days;
            steps = 61;

            available = _allocations[account][index].available();
            reserved = amount.sub(available);
        }
    }

    /**
     * @dev Returns the reserved amount of VOKENs by `account`.
     */
    function reservedOf(address account) public view returns (uint256) {
        uint256 __reserved;

        uint256 __len = _allocations[account].length;
        if (__len > 0) {
            for (uint256 i = 0; i < __len; i++) {
                __reserved = __reserved.add(_allocations[account][i].reserved());
            }
        }

        return __reserved;
    }

    /**
     * @dev Creates `amount` VOKENs and assigns them to `account`.
     *
     * With an `allocation`.
     *
     * Can only be called by a minter.
     */
    function _mintWithAllocation(address account, uint256 amount) internal returns (bool) {
        Allocations.Allocation memory __allocation;

        __allocation.amount = amount;

        _allocations[account].push(__allocation);

        _voken.mintWithAllocation(account, amount, address(this));
        return true;
    }









    /**
     * @dev {Deposit} or {Withdraw}
     */
    function () external payable {
        // deposit
        if (msg.value > 0) {
            _ethers = _ethers.add(msg.value);
            _pageEthers[_page] = _pageEthers[_page].add(msg.value);
        }

        // withdraw
        else if (_isShareholders[msg.sender]) {
            uint256 __vokenHolding;

            for (uint256 i = 1; i <= _page.sub(1); i++) {
                __vokenHolding = __vokenHolding.add(_pageVokenHoldings[i][msg.sender]);

                if (_withdrawPos[msg.sender] < i) {
                    uint256 __etherAmount = _pageEthers[i].mul(__vokenHolding).div(_pageVokenSum[i]);

                    _withdrawPos[msg.sender] = i;
                    _pageEtherDividends[i][msg.sender] = __etherAmount;

                    msg.sender.transfer(__etherAmount);
                    emit Dividend(msg.sender, __etherAmount, i);
                }
            }
        }

        assert(true);
    }

    /**
     * @dev Sets the VOKEN main contract address.
     */
    function setVokenMainContract(IVoken vokenMainContract) public onlyOwner {
        require(address(vokenMainContract) != address(0), "VOKEN: main contract is the zero address");
        _voken = vokenMainContract;
    }

    /**
     * @dev End the current page.
     */
    function endPage() public onlyProxy returns (bool) {
        require(_pageEthers[_page] > 0, "Ethers on current page is zero.");

        _pageEndingBlock[_page] = block.number;

        _page = _page.add(1);
        _pageVokenSum[_page] = _vokens;

        return true;
    }

    /**
     * @dev Push shareholders.
     *
     * Can only be called by a proxy.
     */
    function pushShareholders(address[] memory accounts, uint256[] memory values) public onlyProxy returns (bool) {
        require(accounts.length == values.length, "Shareholders: batch length is not match");

        for (uint256 i = 0; i < accounts.length; i++) {
            address __account = accounts[i];
            uint256 __value = values[i];

            if (!_isShareholders[__account]) {
                _shareholders.push(__account);
                _isShareholders[__account] = true;
            }

            if (!_isPageShareholders[_page][__account]) {
                _pageShareholders[_page].push(__account);
                _isPageShareholders[_page][__account] = true;
            }

            _vokens = _vokens.add(__value);
            _pageVokens[_page] = _pageVokens[_page].add(__value);
            _pageVokenSum[_page] = _vokens;
            _pageVokenHoldings[_page][__account] = _pageVokenHoldings[_page][__account].add(__value);

            assert(_mintWithAllocation(__account, __value));
        }

        return true;
    }
}