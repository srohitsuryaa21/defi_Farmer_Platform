// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ProductTraceability {

    struct Product {
        uint256 id;
        string cropName;
        string quantity;
        string location;
        string harvestDate;
        string price;
        address farmer;
        string status;
    }

    uint256 public productCount = 0;

    mapping(uint256 => Product) public products;

    event ProductCreated(
        uint256 id,
        string cropName,
        address farmer,
        string status
    );

    event ProductStatusUpdated(
        uint256 id,
        string status
    );

    function createProduct(
        string memory _cropName,
        string memory _quantity,
        string memory _location,
        string memory _harvestDate,
        string memory _price
    ) public {

        productCount++;

        products[productCount] = Product(
            productCount,
            _cropName,
            _quantity,
            _location,
            _harvestDate,
            _price,
            msg.sender,
            "Available"
        );

        emit ProductCreated(
            productCount,
            _cropName,
            msg.sender,
            "Available"
        );
    }

    function updateStatus(
        uint256 _id,
        string memory _status
    ) public {

        require(_id > 0 && _id <= productCount, "Invalid Product ID");

        products[_id].status = _status;

        emit ProductStatusUpdated(_id, _status);
    }

    function getProduct(uint256 _id)
        public
        view
        returns (
            uint256,
            string memory,
            string memory,
            string memory,
            string memory,
            string memory,
            address,
            string memory
        )
    {
        Product memory p = products[_id];

        return (
            p.id,
            p.cropName,
            p.quantity,
            p.location,
            p.harvestDate,
            p.price,
            p.farmer,
            p.status
        );
    }
}