/**
 *Submitted for verification at Etherscan.io on 2019-08-11
*/

/**
 *Submitted for verification at Etherscan.io on 2019-08-11
*/

pragma solidity ^0.4.25;

interface IERC20 {
    function totalSupply() constant external returns (uint256 totSupply);
    function balanceOf(address _owner) constant external returns (uint256 balance);
    function transfer(address _to, uint256 _value) external returns (bool success);
    function transferFrom(address _from, address _to, uint256 _value) external returns (bool success);
    function approve(address _spender, uint256 _value) external returns (bool success);
    function allowance(address _owner, address _spender) constant external returns (uint256 remaining);
    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);
}

/**
 * SafeMath library
*/
library SafeMath {
  function mul(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a * b;
    assert(a == 0 || c / a == b);
    return c;
  }

  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a / b;
    return c;
  }

  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    assert(c >= a);
    return c;
  }
}

contract owned {
        address public owner;

        constructor() public {
            owner = msg.sender;
        }

        modifier onlyOwner {
            require(msg.sender == owner);
            _;
        }

        function transferOwnership(address newOwner) onlyOwner public {
            owner = newOwner;
        }
}

contract CarStickerAd is owned,IERC20{
    
    using SafeMath for uint256;
    
    uint256 public _totalSupply = 900000000000000000000000;
 
    string public constant symbol = 'CSA';

    string public constant name = 'CarStickerAd';
    
    uint8 public constant decimals = 18;
    
    mapping(address => uint256) public balances;
    mapping (address => mapping (address => uint256)) allowed;

    /**
     * constructor function
     * add balance to creater address
    */
    constructor() public {
        balances[msg.sender] = _totalSupply;
    }
    
    /**
     * get totalSupply
    */
    function totalSupply() constant external returns (uint256 totSupply){
        return _totalSupply;
    }
   
    /**
     * get balance of an address
    */
    function balanceOf(address _owner) constant external returns (uint256 balance) {
        return balances[_owner];
    }
    
    /**
     * transfer tokens
    */
    function transfer(address _to, uint256 _value) external returns (bool success) {
        require(
            balances[msg.sender] >= _value
            && _value > 0
        );
        
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    function transferFrom(address _from, address _to, uint256 _value) external returns (bool success) {
        require(
            allowed[_from][msg.sender] >= _value
            && balances[_from] >= _value
            && _value > 0  
        );
        balances[_from] = balances[_from].sub(_value);
        balances[_to] = balances[_to].add(_value);
        allowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_value);
        emit Transfer(_from, _to, _value);
        return true;
    }

    function approve(address _spender, uint256 _value) external returns (bool success) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function allowance(address _owner, address _spender) external constant returns (uint256 remaining) {
        return allowed[_owner][_spender];
    }
    
    /**
     * min new token
     */
    function mint(uint256 _value) public onlyOwner {
        _mint(_value);
    }
    
    function _mint(uint256 value) internal onlyOwner {
    
        _totalSupply = _totalSupply.add(value);
        balances[owner] = balances[owner].add(value);
        emit Transfer(owner, address(0), value);
    }
    
    /**
     * Burns a specific amount of tokens.
     */
    function burn(uint256 _value) public {
        _burn(msg.sender, _value);
    }
   
    function _burn(address account, uint256 value) internal {
        require(account != 0);
        require(value <= balances[account]);
    
        _totalSupply = _totalSupply.sub(value);
        balances[account] = balances[account].sub(value);
        emit Transfer(account, address(0), value);
    }
    
    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

}