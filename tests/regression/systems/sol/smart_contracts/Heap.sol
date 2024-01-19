/**
 *Submitted for verification at Etherscan.io on 2019-08-11
*/

pragma solidity ^0.5.10;


contract Ownable {
    address public owner;

    event TransferOwnership(address _from, address _to);

    constructor() public {
        owner = msg.sender;
        emit TransferOwnership(address(0), msg.sender);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "only owner");
        _;
    }

    function setOwner(address _owner) external onlyOwner {
        emit TransferOwnership(owner, _owner);
        owner = _owner;
    }
}

// File: contracts/commons/AddressMinHeap.sol

pragma solidity ^0.5.10;

/*
    @author Agustin Aguilar <[email protected]>
*/


library AddressMinHeap {
    using AddressMinHeap for AddressMinHeap.Heap;

    struct Heap {
        uint256[] entries;
        mapping(address => uint256) index;
    }

    function initialize(Heap storage _heap) internal {
        require(_heap.entries.length == 0, "already initialized");
        _heap.entries.push(0);
    }

    function encode(address _addr, uint256 _value) internal pure returns (uint256 _entry) {
        /* solium-disable-next-line */
        assembly {
            _entry := not(or(and(0xffffffffffffffffffffffffffffffffffffffff, _addr), shl(160, _value)))
        }
    }

    function decode(uint256 _entry) internal pure returns (address _addr, uint256 _value) {
        /* solium-disable-next-line */
        assembly {
            let entry := not(_entry)
            _addr := and(entry, 0xffffffffffffffffffffffffffffffffffffffff)
            _value := shr(160, entry)
        }
    }

    function decodeAddress(uint256 _entry) internal pure returns (address _addr) {
        /* solium-disable-next-line */
        assembly {
            _addr := and(not(_entry), 0xffffffffffffffffffffffffffffffffffffffff)
        }
    }

    function top(Heap storage _heap) internal view returns(address, uint256) {
        if (_heap.entries.length < 2) {
            return (address(0), 0);
        }

        return decode(_heap.entries[1]);
    }

    function has(Heap storage _heap, address _addr) internal view returns (bool) {
        return _heap.index[_addr] != 0;
    }

    function size(Heap storage _heap) internal view returns (uint256) {
        return _heap.entries.length - 1;
    }

    function entry(Heap storage _heap, uint256 _i) internal view returns (address, uint256) {
        return decode(_heap.entries[_i + 1]);
    }

    // RemoveMax pops off the root element of the heap (the highest value here) and rebalances the heap
    function popTop(Heap storage _heap) internal returns(address _addr, uint256 _value) {
        // Ensure the heap exists
        uint256 heapLength = _heap.entries.length;
        require(heapLength > 1, "The heap does not exists");

        // take the root value of the heap
        (_addr, _value) = decode(_heap.entries[1]);
        _heap.index[_addr] = 0;

        if (heapLength == 2) {
            _heap.entries.length = 1;
        } else {
            // Takes the last element of the array and put it at the root
            uint256 val = _heap.entries[heapLength - 1];
            _heap.entries[1] = val;

            // Delete the last element from the array
            _heap.entries.length = heapLength - 1;

            // Start at the top
            uint256 ind = 1;

            // Bubble down
            ind = _heap.bubbleDown(ind, val);

            // Update index
            _heap.index[decodeAddress(val)] = ind;
        }
    }

    // Inserts adds in a value to our heap.
    function insert(Heap storage _heap, address _addr, uint256 _value) internal {
        require(_heap.index[_addr] == 0, "The entry already exists");

        // Add the value to the end of our array
        uint256 encoded = encode(_addr, _value);
        _heap.entries.push(encoded);

        // Start at the end of the array
        uint256 currentIndex = _heap.entries.length - 1;

        // Bubble Up
        currentIndex = _heap.bubbleUp(currentIndex, encoded);

        // Update index
        _heap.index[_addr] = currentIndex;
    }

    function update(Heap storage _heap, address _addr, uint256 _value) internal {
        uint256 ind = _heap.index[_addr];
        require(ind != 0, "The entry does not exists");

        uint256 can = encode(_addr, _value);
        uint256 val = _heap.entries[ind];
        uint256 newInd;

        if (can < val) {
            // Bubble down
            newInd = _heap.bubbleDown(ind, can);
        } else if (can > val) {
            // Bubble up
            newInd = _heap.bubbleUp(ind, can);
        } else {
            // no changes needed
            return;
        }

        // Update entry
        _heap.entries[newInd] = can;

        // Update index
        if (newInd != ind) {
            _heap.index[_addr] = newInd;
        }
    }

    function bubbleUp(Heap storage _heap, uint256 _ind, uint256 _val) internal returns (uint256 ind) {
        // Bubble up
        ind = _ind;
        if (ind != 1) {
            uint256 parent = _heap.entries[ind / 2];
            while (parent < _val) {
                // If the parent value is lower than our current value, we swap them
                (_heap.entries[ind / 2], _heap.entries[ind]) = (_val, parent);

                // Update moved Index
                _heap.index[decodeAddress(parent)] = ind;

                // change our current Index to go up to the parent
                ind = ind / 2;
                if (ind == 1) {
                    break;
                }

                // Update parent
                parent = _heap.entries[ind / 2];
            }
        }
    }

    function bubbleDown(Heap storage _heap, uint256 _ind, uint256 _val) internal returns (uint256 ind) {
        // Bubble down
        ind = _ind;

        uint256 lenght = _heap.entries.length;
        uint256 target = lenght - 1;

        while (ind * 2 < lenght) {
            // get the current index of the children
            uint256 j = ind * 2;

            // left child value
            uint256 leftChild = _heap.entries[j];

            // Store the value of the child
            uint256 childValue;

            if (target > j) {
                // The parent has two childs 👨‍👧‍👦

                // Load right child value
                uint256 rightChild = _heap.entries[j + 1];

                // Compare the left and right child.
                // if the rightChild is greater, then point j to it's index
                // and save the value
                if (leftChild < rightChild) {
                    childValue = rightChild;
                    j = j + 1;
                } else {
                    // The left child is greater
                    childValue = leftChild;
                }
            } else {
                // The parent has a single child 👨‍👦
                childValue = leftChild;
            }

            // Check if the child has a lower value
            if (_val > childValue) {
                break;
            }

            // else swap the value
            (_heap.entries[ind], _heap.entries[j]) = (childValue, _val);

            // Update moved Index
            _heap.index[decodeAddress(childValue)] = ind;

            // and let's keep going down the heap
            ind = j;
        }
    }
}

// File: contracts/Heap.sol

pragma solidity ^0.5.10;



contract Heap is Ownable {
    using AddressMinHeap for AddressMinHeap.Heap;

    // heap
    AddressMinHeap.Heap private heap;

    // Heap events
    event JoinHeap(address indexed _address, uint256 _balance, uint256 _prevSize);
    event LeaveHeap(address indexed _address, uint256 _balance, uint256 _prevSize);

    uint256 public constant TOP_SIZE = 512;

    constructor() public {
        heap.initialize();
    }

    function topSize() external pure returns (uint256) {
        return TOP_SIZE;
    }

    function addressAt(uint256 _i) external view returns (address addr) {
        (addr, ) = heap.entry(_i);
    }

    function indexOf(address _addr) external view returns (uint256) {
        return heap.index[_addr];
    }

    function entry(uint256 _i) external view returns (address, uint256) {
        return heap.entry(_i);
    }

    function top() external view returns (address, uint256) {
        return heap.top();
    }

    function size() external view returns (uint256) {
        return heap.size();
    }

    function update(address _addr, uint256 _new) external onlyOwner {
        uint256 _size = heap.size();

        // If the heap is empty
        // join the _addr
        if (_size == 0) {
            emit JoinHeap(_addr, _new, 0);
            heap.insert(_addr, _new);
            return;
        }

        // Load top value of the heap
        (, uint256 lastBal) = heap.top();

        // If our target address already is in the heap
        if (heap.has(_addr)) {
            // Update the target address value
            heap.update(_addr, _new);
            // If the new value is 0
            // always pop the heap
            // we updated the heap, so our address should be on top
            if (_new == 0) {
                heap.popTop();
                emit LeaveHeap(_addr, 0, _size);
            }
        } else {
            // IF heap is full or new balance is higher than pop heap
            if (_new != 0 && (_size < TOP_SIZE || lastBal < _new)) {
                // If heap is full pop heap
                if (_size >= TOP_SIZE) {
                    (address _poped, uint256 _balance) = heap.popTop();
                    emit LeaveHeap(_poped, _balance, _size);
                }

                // Insert new value
                heap.insert(_addr, _new);
                emit JoinHeap(_addr, _new, _size);
            }
        }
    }
}