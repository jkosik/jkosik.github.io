---
title: "Decentralised application (dApp) on Ink Blockchain powered by Smart contracts"
date: 2025-11-08T8:15:05+07:00
slug: dApp
description: How to use blockchains and Smart contracts to set up fast, cheap, tamper-proof peer-to-peer contractual relations without need for a middlemen.
image: images/motivateme/big.png
categories:
  - tech
tags: # "feature" tag tops the post
  - crypto
draft: false
---

Curious how Layer 2 Ethereum-based blockchains and Smart Contracts come together to power decentralized apps (dApps)?
In this post, we will explore those principles in action by building a simple educational dApp [Motivateme](https://motivateme.ink).

If you are already familiar with the buzzwords above, feel free to jump straight in https://motivateme.ink or explore the code at https://github.com/jkosik/motivateme and dive deeper.

If terms like Ethereum, Smart Contracts, Layer 1 or Layer 2 blockchain sound new — don’t worry. Keep reading, and we will break it all down in plain English.

## TLDR Summary
The project [Motivateme](https://motivateme.ink):
1. Deploys Smart contract on a Layer 2 Ethereum-based blockchain.
2. Builds a web application, which interacts with the Smart contract.
3. Allows people to motivate others by locking the award in ETH cryptocurrency and let Smart contract release the award when conditions defined in the Smart contract are met.

This is the entire application workflow is depicted in the following graphics.
{{< figure src="images/motivateme/flow.png" >}}


## dApp properties
Core of the **dApp (decentralised application)** is a Smart contract - a programatic version of a classic contract as we know from the physical world, however stored on the decentralised, tamper-proof blockchain.
Even though Smart contract is the core component of the dApp, full-blown dApp could contain also further properties of decentralisation:
- Application hosted on decentralised infrastructure like [IPFS filesystem](https://ipfs.tech/).
- Permission-less frontend with no backend user management.
- Decentralised and community-driven governance.
- Decentralised arbiter who validates whether all conditions of the Smart contracts were met. Some contract conditions can be auto-validated by hardcoding them inside the Smart contract. Sometimes validation depends on events from the physical world, outside of blockchain. This problem is also resolved and addressed through [validation Oracles](https://chain.link/education/blockchain-oracles).

Our **MotivateMe** dApp primarily focuses on Smart contracts and does not incorporate Oracles or advanced validation mechanisms. Instead, it relies on social accountability, using transparent on-chain tracking of user actions as the main form of validation.

Interacting with Smart Contracts on the blockchain isn’t free and not every blockchain supports them. One of the most common environments for hosting Smart Contracts are Layer 2 blockchains built on top of Ethereum blockchain. In our case, we will be using exactly that - the [Ink blockchain](https://inkonchain.com/).

## L1 and L2 blockchains
Bitcoin or Ethereum are well-known Layer 1 blockchains. They act as a backbone for crypto transactions. Some blockchains like Bitcoin are primarily designed for transacting cryptocurrency, later extended by other functionalities though.

As blockchain adoption grew, some limitation were discovered, mainly transaction speed and cost. At the same time, new use cases were identifed, such as storing NFTs or building Smart contracts. That is where Layer 2 (L2) blockchains come in and fill in the gap.

L2 networks operate their own set of nodes to quickly process and sequence transactions before submitting them in batches to Layer 1 (L1) for final confirmation. This setup even allows rollbacks on L2 if required by L1. Despite that flexibility, L2 blockchains have already robust fraud-prevention mechanisms that keep the system secure.

### Layer 2 characteristics
Layer 2 blockchains are connected to their parent Layer 1 blockchain. One common method of interconnection is through **rollups**, where L2 transactions are bundled and compressed off-chain before being submitted to L1.

[This article](https://www.cyfrin.io/blog/what-are-blockchain-rollups-a-full-guide-to-zk-and-optimistic-rollups?utm_source=chatgpt.com) provides a detailed explanation of the two main types of rollups:
- Optimistic rollups
- Zero-knowledge rollups

L2 chains are extensions of L1 chains and address:
- improved blockchain scalability
- lower transaction fees
- faster transactions
- interoperability of special-purpose L2 chains

**MotivateMe** dApp uses [Ink L2 blockchain](https://inkonchain.com/) which is the implementation of [OP Mainnet L2 blockchain](https://www.optimism.io/). 
OP Mainnet is built on top of the Ethereum Layer 1 blockchain, leveraging its security and settlement capabilities.
OP Mainnet’s long-term vision is to create an interoperable network of L2 chains - a connected ecosystem known as the **Superchain**.

Even though **MotivateMe** is deployed on the Ink L2 blockchain, it could be easily hosted on OP Mainnet and even directly on Ethereum L1 blockchain without any significant code changes.

**Are L2 blockchains as decentralised as Layer 1?**  
Not entirely. Most Layer 1 blockchains have thousands of transaction validators (or miners) maintaining the network. In contrast, Layer 2 blockchains are usually operated by a core team that runs the L2 nodes and relies on centralized **Sequencers** to collect transactions and submit them to the fully decentralized Layer 1 network.

**Where is my crypto stored on Layer 2?**  
A Layer 2 blockchain is a physically separate network. Your funds on one L2 are independent from those on other L2 blockchains, as well as from your funds on the Layer 1 blockchain.

Let me depict this concept on an example:
1. You have 10 ETH on L1 Ethereum blockchain.
2. You have to use L2 bridge, e.g. [Ink bridge](https://inkonchain.com/bridge), to transfer 10 L1 ETHs to L2. 
In reality, **10 ETHs are locked on L1 using the L2 rollup Smart contract** - remember this concept, since later on we will also use "locking" and "Smart contract" in our dApp. 
3. Corresponding `wrapped` ETH tokens are issued on L2 chain and can be transacted on that particular L2 chain.

Important: Your wallet address remains the same across both layers (since they are both Ethereum-based), but your balances differ because each layer operates on its own blockchain.

## Smart Contract
In a real world, classic contract is a written document with rights and liabilities of contracted parties. Limitations of a standard contract are clear and described in the follwing table:

| Classic contract                                                         | Smart contract                                                |
|--------------------------------------------------------------------------|---------------------------------------------------------------|
| Not reusable. Requires separate (printed) instance for new cases.        | Single reusabe contract stored on the blockchain.             |
| Requires trusted party to confirm signatures.                            | No middleman is needed. Trust based on cryptography.          |
| Requires safe storage.                                                   | Stored decentrally on the blockchain.                         |
| Identity of contracting parties can be faked.                            | Tamper-proof identities.                                      |
| Contract contents can be faked.                                          | Tamper-proof contents.                                        |
| Written as a static text.                                                | Written in programming language supporting complex logic.     |
| Interpreted by (potentially biased) lawyer.                              | Interpreted by a computer with no room for misinterpretation. |

Smart contract support also very complex use cases, as [minting own cryptocurrency as described in one of my previous blogs](https://jkosik.github.io/posts/crypto/).

**How exactly the Smart contract looks like?**  
This is a minimalistic Smart contract example provided by Ethereum Development Framework [Foundry](https://getfoundry.sh/):
```
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

contract Counter {
    uint256 public number;

    function increment() public {
        number++;
    }
}
```

This Smart contract has two "contract stipulations":
1. Callable variable **number** which can be read anytime. Similarly to reading a paragraph in a classic contract.
2. Callable function **increment** which increments a **number** variable. Similarly to activating a paragraph in a classic contract when contract conditions were met.

**How is the Smart Contract executed?**  
By triggering the code. The code is executed on [Ethereum Virtual Machine (EVM)](https://ethereum.org/developers/docs/evm/) running on Ink blockchain Sequencer nodes. *For L1 networks, EVM runs on every Ethereum validation node.*  
Execution is triggered by a call to a blockchain RPC endpoint - for Ink blockchain it is https://rpc-gel.inkonchain.com. Call can be executed by any user using Foundry client `cast` or through dApps user intereface.

**How to develop a Smart contract?**  
Classic contracts are first drafted and only then finalised. The same is possible on the blockchain. Instead of writing the contract and deploying on the blockchain immediately, you have a blockchain playground available. Each blockchain has a Mainnet, where the real transactions happen and also a Testnet or Devnet, where artificial transaction can be simulated and everything is free of charge there.
Also Ink has a Testnet and the test RPC endpoint is https://ink-sepolia.drpc.org. [MotivateMe README.md](https://github.com/jkosik/motivateme/blob/main/README.md) explains the entire development process, including generating of fake ETHs for transacting on Testnet.


## MotivateMe dApp
https://motivateme.ink dApp implements Smart contract with three simple educational motivational use cases. The sender sets the motivation (or challenge) for the recipient and lock a prize money. If the conditions are met and challenge is fulfiled, reward are unlocked and released to the recipient.

MotivateMe implements these 3 motivations:
{{< figure src="images/motivateme/select-motivation.png" >}}

1. Sender can unconditionally and immediately send money to another Ink wallet.
2. The sender can lock the reward for a specific number of days. After that period, the eligible recipient can claim the funds by interacting with the Smart Contract - either directly via blockchain CLI client or through the dApp.
3. The sender can lock the reward, and the recipient must then submit proof of completing the challenge through the dApp. Currently, the application only requests a simple text confirmation, but the dApp could implement its own proof-validation logic or integrate Oracles for more complex verification.



### Cryptography
Cryptography ensures, that only the eligible recipients defined by the sender can claim the reward.

**How is sender's and recipient's identity validated?**  
On the blockchain, trust is ensured by [asymmetric cryptography](https://en.wikipedia.org/wiki/Public-key_cryptography) which is built around a private and public key-pairs. Private key is used for proving the identity and signing the trasactions and public key is used for identifying the parties.

In our case, the sender's motivations are signed by the sender's private key and locked for a recipient's public key.
To be fully technically precise, the recipient is identified by this wallet address, which is derived from recipient's public key. The entire flow looks like this:
```
Private Key → Public Key → Wallet Address
```

When you are generating a wallet on Ethereum-compatible blockchain, like OP Mainnet or Ink, you generate a private key, which generates a corresponding public key, building a key-pair. Public key is then hashed and shortened and generates a wallet address composed of 40 hexadecimal characters, e.g. `0x4fcC5C461B59ECC4786CDa6Ec270bA29Eb657FAF`. Also a Smart contract itself has its own dedicated wallet address and all contract interactions are executes against that address. 

Each Smart contract interaction is in fact a blockchain transaction and each transaction has to be authenticated using the private key. When using CLI, we export our wallet's private key and run **cast**. In the following example, we initiate the call to the **increment** function of our testing Smart contract deployed on Ink Testnet:
```
export $WALLET_PRIVATE_KEY=0xABCD...

cast send 0x4fcC5C461B59ECC4786CDa6Ec270bA29Eb657FAF "increment()" \
  --rpc-url https://ink-sepolia.drpc.org \
  --private-key $WALLET_PRIVATE_KEY
```
  
Details of this transaction can be found in the CLI as well as in the blockchain explorer: https://explorer.inkonchain.com/address/0x4fcC5C461B59ECC4786CDa6Ec270bA29Eb657FAF?tab=txs (see the **increment** in the Method column)

{{< figure src="images/motivateme/transaction-testnet.png" >}}

### dApp authentication
Smart contract can be deployed and interacted with directly via CLI and blockchain RPC endpoint. dApp improves user experience by friendly abstraction layer and can integrate nicely by one of authentication SDKs, like [WalletConnect](https://docs.walletconnect.network/), recently wrapped and rebranded as [Reown](https://docs.reown.com/appkit/overview).

These SDKs offer easy integration with crypto wallets in browser extension or even with mobile wallets - MotivateMe supports both. Wallet private keys are stored in the browser's secure storage or in the mobile device. Linking the wallet to dApp is a one click operation or a simple QR code scan using a smart phone camera.

<video controls playsinline width="800" poster="/images/fallback.jpg">
  <source src="https://mintcdn.com/reown-5552f0bb/mrXva7Pfcna94qcp/images/appkit-overview-demo.mp4?fit=max&auto=format&n=mrXva7Pfcna94qcp&q=85&s=b212237900c8ca324660b3ed38eea8d2
  " type="video/mp4">
  Sorry, your browser doesn’t support embedded videos.
</video>

### "What happens on the blockchain stays on the blockchain."
One of our motivation types is a Proof-of-Action motivation where the sender requires specific action and recipient proves the execution before reward is released. Both sender's requirement and claimant's proof are stored directly on the blockchain:

1. Sender stores the motivation on the blockchain requesting execution from a particular (recipient's) wallet address **0xDda568a3fc17d2377eb73c8EB6aB965eF7ED1f09**:
```
Dear Developer ABC,
Please submit a pull request for project XYZ for 0.0001 ETH and assist us in fixing the code.
Thank you.
```

{{< figure src="images/motivateme/proof-requested-ui.png" >}}

Once the motivation is created and confirmed in the sender's crypto wallet, transaction with the requirement defintion and eligible recipient address **0xDda568a3fc17d2377eb73c8EB6aB965eF7ED1f09** is recorded on the blockchain:
```
✅ Proof-of-action motivation created in block 29187956
```

The transaction detail can be inspected here: https://explorer.inkonchain.com/tx/0xfdb049a30d81d0572db7a93d24e62eb64bc2d611c015a22c98d2225572a95817

{{< figure src="images/motivateme/proof-requested.png" >}}


2. The recipient completes the challenge and submits proof of completion. Submitting the proof and claiming the reward is a new blockchain transaction.  
In our case, the proof is socially enforced, meaning there is no automated validation on-chain. However, in a more advanced implementation, this could be extended with programmatic validation within the dApp or through dedicated Oracles.   
For now, the recipient (claimant) simply provides a textual proof in the dApp to which he authenticates by linking his wallet.

{{< figure src="images/motivateme/proof-submitted-ui.png" >}}

```
✅ Proof-of-action motivation claimed in block 29188192
```

The transaction detail can be inspected here: https://explorer.inkonchain.com/tx/0x04a975dbaec593906a2964dc22a3e2392ee67a57d5b7a6a84330c5eb64bef689

{{< figure src="images/motivateme/proof-submitted.png" >}}

## Closing words
For more details check https://github.com/jkosik/motivateme. It includes additional information on interacting with the blockchain via the command line, as well as the full dApp source code, Smart Contract code, and deployment code using Ansible and Kubernetes.

Looking ahead, Smart Contracts represent far more than a way to send or lock digital funds. They are the foundation for automated, trustless agreements that can reshape industries. Smart Contracts are evolving into a powerful tool for building transparent, self-executing systems without intermediaries.

As Layer 2 networks mature and scalability improves, Smart Contracts will likely become the core logic layer of the decentralized web, enabling seamless, programmable interactions between users, organizations, and applications. The journey is just beginning and projects like MotivateMe demonstrate how even simple use cases can help pave the way toward a more open and automated digital future.