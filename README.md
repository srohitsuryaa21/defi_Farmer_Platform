# DeFi Farmer Platform

DeFi Farmer Platform is a hybrid web + blockchain application designed to support small-scale farmers through transparent product traceability and a simple buyer marketplace.

The platform allows farmers to register, add agricultural product batches, and sync those batches to an Ethereum smart contract. Buyers can browse available products, purchase them, and view traceability details. The application stores normal platform data in SQLite and important product lifecycle records on a local Ethereum blockchain using Ganache.

## Features

### User Management
- Farmer registration and login
- Buyer registration and login
- Secure password hashing using Werkzeug

### Farmer Features
- Add product batches
- View all own products
- See blockchain sync status
- View blockchain product count
- Access traceability details

### Buyer Features
- View available product batches
- Purchase products
- View purchased products
- Access traceability details

### Blockchain Features
- Product creation synced to Ethereum smart contract
- Blockchain product ID stored in SQLite
- Product sale status updated on-chain
- Product trace page shows both database and blockchain records

## Tech Stack

### Backend
- Python
- Flask
- SQLite

### Frontend
- HTML
- Bootstrap 5

### Blockchain
- Solidity
- Ganache
- Web3.py
- Remix IDE

## Project Structure

```bash
defi-farmer-project/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── contracts/
│   └── ProductTraceability.sol
│
├── blockchain/
│   ├── contract_address.txt
│   ├── connect_test.py
│   ├── blockchain_utils.py
│   └── abi/
│       └── ProductTraceability.json
│
├── database/
│   └── app.db
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/
    ├── index.html
    ├── register.html
    ├── login.html
    ├── add_product.html
    ├── farmer_dashboard.html
    ├── buyer_dashboard.html
    └── product_detail.html
```

How It Works

The platform follows a hybrid architecture:

The user interacts with the web interface built using Flask templates and Bootstrap.
Farmers add product batches through the web form.
Product details are stored in SQLite for normal application use.
At the same time, product data is written to the Ethereum smart contract on Ganache.
The blockchain product ID is stored in the database to maintain linkage between off-chain and on-chain records.
When a buyer purchases a product, the product status is updated in SQLite and also updated on-chain using the smart contract.
The traceability page displays:
database product data
buyer/farmer details
blockchain product details
blockchain status
Smart Contract Overview

The main smart contract used in this project is:

ProductTraceability.sol

It provides functions for:

creating a product
updating product status
reading product data
checking total blockchain product count
Setup Instructions
1. Clone the repository
git clone <your-repo-link>
cd defi-farmer-project
2. Create virtual environment
python -m venv venv
3. Activate virtual environment
Windows PowerShell
.\venv\Scripts\Activate.ps1

If blocked:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
4. Install dependencies
pip install -r requirements.txt
5. Start Ganache
Open Ganache
Start a Quickstart Ethereum workspace
Keep Ganache running
6. Deploy smart contract
Open Remix IDE
Compile ProductTraceability.sol
Connect Remix to Ganache using Dev - Ganache Provider
Deploy the contract
Copy the deployed contract address
Save it in:
blockchain/contract_address.txt
Copy the ABI
Save it in:
blockchain/abi/ProductTraceability.json
7. Run the Flask application
python app.py
8. Open in browser
http://127.0.0.1:5000
Testing Flow
Farmer flow
Register as Farmer
Login
Add product batch
Check dashboard for blockchain sync
Open traceability page
Buyer flow
Register as Buyer
Login
View available products
Buy a product
Check purchased products
Open traceability page
Important Notes
Ganache must remain running while using blockchain features.
If Ganache is restarted or a new workspace is created, the contract may need to be redeployed and the contract address updated.
The ABI file usually remains the same unless the smart contract code changes.
SQLite is used for local development and demo purposes.
Current Status

This project currently includes:

working user authentication
product marketplace workflow
product buying flow
blockchain product sync
blockchain sale status sync
UI improved with Bootstrap
Future Improvements
payment smart contract integration
real wallet mapping for users
admin verification module
advanced product lifecycle statuses
improved analytics dashboard
deployment on public Ethereum-compatible testnet
Inspiration

This project is based on the concept of empowering small-scale farmers with decentralized finance and Ethereum smart contracts for supply-chain transparency and trust.

Author

Rohit Suryaa
