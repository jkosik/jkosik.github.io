---
title: "wherecoinsgo.org - blockchain-based fund raising platform backed by Mempool and Blockscout"
date: 2026-09-24T20:30:00+02:00
slug: wherecoinsgo
description: A crypto fund raising platform can be more transparent than conventional platforms, because the whole history sits on a public ledger. Bitcoin through mempool.space and all other blockchains through Blockscout.
image: images/wherecoinsgo/big.png
categories:
  - tech
tags:
  - blockscout
  - blockchain
  - crypto
draft: false
---

I built [wherecoinsgo.org](https://wherecoinsgo.org) to demonstrate benefits of blockchain in the area of donation and transparency account platforms. Conventional systems oftentimes offer illusion of transparency and provide only one layer deep visibility and mostly onlu on sender side, not tracking expenditures at all. Moreover, the identity of senders and receivers is mostly very vague and not directly trusted, othentimes just an arbitrarily written name or bank account number with no attribution to the origin of the money.

On a public blockchain the whole history is already there. In, out, what is left. Anyone can look, later, without asking permission.

## Wherecoinsgo
[wherecoinsgo.org](https://wherecoinsgo.org) offers two key features:

#### 1. Fund raising
Offers one-click creation of own Wherecoinsgo **projects** with **shareable paylinks** and QR codes, **balance views** and **transaction history** for transparent fund raising.

{{< figure src="images/wherecoinsgo/paylink.png" >}}

#### 2. User-friendly blockchain explorer
Acts as an easy to use public interface for browsing the blockchain and transactions related to the submitted crypto wallet on Bitcoin, Ethereum and [Ink](https://inkonchain.com/) blockchain. Also tracks suspicious intermediaries can be spotted using integrated [sanction list](https://ofac.treasury.gov/).

{{< figure src="images/wherecoinsgo/diagram.png" >}}

On top of these features, you can build charity programs, donation services, transpranecy accounts for public funding and more.

## Wherecoinsgo vs "traditional" fundraising
| Feature | Wherecoinsgo | Traditional fund raising |
|---|---|---|
| Transaction drilldown | Infinite - follow any coin back to its origin | One layer deep - only the direct sender |
| Money flow direction | Bidirectional - see both received and spent funds | Usually one-directional - inflows are shown, spending needs a separate report/audit |
| Access | Public, permissionless - anyone can look, anytime, no approval needed | Private by default - statements require permission, NDA, or a formal audit request |
| Custody of funds | Non-custodial - money moves wallet-to-wallet, the platform never holds it | Custodial - the platform/bank holds and controls the funds, with chargeback/fee/freeze risk |
| Timeliness | Real-time - every confirmed block updates the picture instantly | Periodic - annual reports or audits, often months delayed |
| Reach | Borderless - anyone with a wallet can give or verify, no bank account or KYC needed | Geographically and institutionally gated - banking rails, KYC, cross-border friction |

## Multi-chain
What is multi-chain?
Multi-chain architecture offers wider options for the customers. People can collect funds on various blockchains - Bitcoin, Ethereum, Ink...Potentially you could fund your project by collecting even [meme coins](https://coinmarketcap.com/view/memes/).

Ethereum and Ink are EVM-based blockchains and they use the same addresses, however the balances on each are different. See this example for the address `0x000000000000000000000000000000000000dEaD`
- Ink blockchain: https://wherecoinsgo.org/inspect?address=0x000000000000000000000000000000000000dEaD&chain=ink
- Ethereum blockchain: https://wherecoinsgo.org/inspect?address=0x000000000000000000000000000000000000dEaD&chain=ethereum

That can be surprising details for beginners looking for "lost" funds.

## Blockscout and Mempool
To interact with the blockchain and get the transaction data, we could run own blockchain node and index all transactions for later lookups OR we could utilise existing **blockchain explorers** with mature API endpoints. The second options is definitely much better.

For Bitcoin, I selected traditionally [mempool.space](https://mempool.space) and the rest of the lookups are funnelled through [Blockscout](https://www.blockscout.com/). Blockscout offers nice advantage of supporting wide range of blockchains which simplifies the platform architecture and the code is more slim and unified. We do not have to use too many 3rd party API endpoints. All the heavy lifting is done by Blockscout and expanding the product to further blockchains will be very easy.

## What Wherecoinsgo is not
[wherecoinsgo.org](https://wherecoinsgo.org) is not a forensics tool. I say that to myself when the transaction diagram looks too neat. Application always relies on underlying data and does not hide the fact, that is powered by Mempool and Blockscout and advanced users can still use direct hyperlinks and dive as deep as needed in the underlying blockchain explorers.

Instead, [wherecoinsgo.org](https://wherecoinsgo.org) focuses on:
- easy registration and fund raising project creation
- user-friendly UI also for crypto beginners
- appealing fund-raising capabilities by embedding donation buttons to your website, shareable paylinks or payment via QR code.

## Quickstart
https://wherecoinsgo.org/login

*[wherecoinsgo.org](https://wherecoinsgo.org) is a solo project by [Juraj Kosik](https://sk.linkedin.com/in/jurajkosik)*
