---
title: "Crypto donation and transparency account platform using Blockscout API"
date: 2026-09-24T20:30:00+02:00
slug: wherecoinsgo
description: A crypto donation platform is more transparent than the conventional funding, because the whole history sits on a public chain and anyone can follow it. wherecoinsgo.org turns that into a readable page. Bitcoin through mempool.space, Ethereum and Ink through Blockscout.
image: images/wherecoinsgo/big.png
categories:
  - tech
tags:
  - blockscout
  - ethereum
  - ink
  - crypto
draft: true
---

I built [wherecoinsgo.org](https://wherecoinsgo.org) because a donation in crypto can do something a normal donation cannot. A bank wire or a card payment disappears into an organisation's books. You send money, you maybe get a receipt, and after that you take their word for where it went. On a public chain the whole history is already there. In, out, what is left. Anyone can look, later, without asking permission.

The site is just a readable page on top of that. Paste a wallet, pick a chain, see where the coins went. I do not hold the money and I do not hold keys. Bitcoin first, because that is the chain people outside this industry actually know. Ethereum and Ink (Kraken's L2) as well, because plenty of wallets are `0x`.

Most Blockscout users I see are on wallets, dashboards, trading bots. This is a different use of the same API. A treasurer or a donor who will not open a raw explorer for fun.

Three chains, two adapters. Bitcoin through [mempool.space](https://mempool.space). Ethereum and Ink through Blockscout. A trail does not jump chains. A bridge is an endpoint on the chain it left, nothing more.

## Hi Juraj! What does wherecoinsgo.org do, and how does it work?

Paste an address, pick a chain, get a page. The question is **where did the coins go?**

Bitcoin is the default in the picker. Ethereum and Ink appear when someone pastes a `0x`. You have to keep the chain next to the address. A `bc1...` is only Bitcoin. The same `0x...` is valid on Ethereum and on Ink, and the balances are not the same. I have watched people miss that, so every page prints the chain name at the top. I also do not glue a Bitcoin trail onto an EVM one. Looks nice. Would be false.

Anyone can inspect. No account. One box, one button (*Make it transparent*). That view is for the person who opened it. I do not turn a stranger's wallet into a public "account" just because someone looked. If you want to own the page, you sign in with a code I email you, attach a wallet, maybe publish. Pro gets a short pay link, `wherecoinsgo.org/ocean-relief`. Donors pay wallet to wallet, QR and a payment URI. If the app creates a wallet, that happens in the browser. The seed does not come to my server.

The page should read like a short report. Wallet in the middle. Money left to right. **Received** on the left, you can drill. **Spent** on the right, one level, plus what is still there. Left total is Received. Right total is Spent plus Balance. If those disagree I have a bug. I have had that bug. Usually I had forgotten internal transactions on Ink.

Confirmed transfers only. No clustering, no "smart money", no "this is probably an exchange". If mempool.space or Blockscout did not index it, it is not on the picture. A donor can click the hop and check me.

## You are on more than one chain. Where does Blockscout sit?

No vendor SDK. There is a small `Chain` interface in Go: validate, summary, ranked counterparties, history. Each chain has its own HTTP client, cache, and throttle. Adding a chain should be another config row. Today:

| Chain | What I read | What the user clicks |
| --- | --- | --- |
| Bitcoin | [mempool.space](https://mempool.space) Esplora (`/address`, `/txs`, chain stats) | mempool.space |
| Ethereum | Blockscout account API (`balance`, `txlist`, `txlistinternal`) | [eth.blockscout.com](https://eth.blockscout.com) |
| Ink | Blockscout PRO unified API (`api.blockscout.com/v2/api?chainid=57073`) | [explorer.inkonchain.com](https://explorer.inkonchain.com) |

Bitcoin first is not a slogan. It is the chain my parents would recognise, and mempool.space already gives lifetime received and spent, not a "last N transactions" window. Blockscout does not index Bitcoin. I did not pretend it does. mempool.space is the Bitcoin half. Saying that here is fine.

**Blockscout is the EVM half.** Ethereum and Ink share one adapter. Same address shape, same account module. Config is chain ID, `apiBase`, and the public explorer URL. Ink's official explorer is Blockscout. On Ethereum the hop link is [eth.blockscout.com](https://eth.blockscout.com). In theory a new EVM network is a key and a chain ID. I do not run a node. I started an Ink specific client one weekend and deleted it when I noticed it was the Ethereum file with different constants.

Esplora for Bitcoin. Blockscout for EVM, including L2s, so I do not pick up a new vendor every time another OP Stack chain appears.

One inspect on EVM is three calls:

- `module=account&action=balance` (native balance, this one is exact)
- `action=txlist` (outer transactions)
- `action=txlistinternal` (value that moved inside contracts)

I got the third one wrong first. ETH that arrives through a bridge or a deposit contract does not show in `txlist`. Skip internals and an Ink page under counts Received, then it disagrees with explorer.inkonchain.com. A donor will find that for you. I merge both lists, drop failed txs and zero value calls (an `approve` is not a payment), and draw that.

Same client does the rest. The tree is lazy. First paint is the root, one inflow layer, one outflow layer. Deeper is on click. A watcher in the background hits the same adapters, same cache, same throttle, and writes confirmed transfers. I do not have a second indexer for payments. That is how you get two numbers that do not match.

Blockscout setup was dull. `apiBase` in YAML, API key in env, a rate cap. Their PRO free tier is 5 requests per second. Ink is set to that. Cache hits do not count. Next Blockscout chain is another YAML row. Bitcoin stays a mempool.space row. Dull is good.

## Why Blockscout, and not some other explorer API or a paid intel feed?

Ethereum and Ink are different ledgers that share a `0x` prefix. Blockscout already indexes both, and a pile of other EVM networks, with the same account module. I did not want an Ethereum vendor plus an L2 vendor plus a slide about "the next chain". One adapter. Either a per instance host or `api.blockscout.com` with a `chainid`. Bitcoin needs Esplora, so it has mempool.space. Putting Bitcoin through the EVM client would have been cute for a post and stupid in the code.

I also need a URL. A Chainalysis style feed will sell an entity graph. It will not give a treasurer a link she can put in an email that shows the same transfer I drew. Blockscout gives the JSON and the page. If the hop in the tree is not the hop on eth.blockscout.com or explorer.inkonchain.com, "check it yourself" is empty.

People paste a hash, or a chain name, or neither. They do not show up with a vendor account. Blockscout resolves the address and gives a page to hang off it.

I am not building a forensics tool. I say that to myself when the tree looks too neat. Those feeds sell scores to compliance teams. Different buyer. I need what a public explorer already knows, at a cost I can predict, with a name on it. If a node ever gets an address tag it will say `via Blockscout`. Not "I identified this person". I do not identify people.

I looked at running nodes. No. Not for something I run alone that has to do Bitcoin and two EVM chains. I also looked at one mega vendor for everything. Nobody honest is the best Bitcoin explorer and the best OP Stack explorer at the same time. Two public APIs. mempool.space when it is Bitcoin. Blockscout when it is EVM.

## What was the hard part? Did things break?

Talking to `/api` is easy. Staying honest when the wallet is a mess is not.

Internals on L2s, again. `txlist` only looked fine on a boring Ethereum EOA. Anything that had touched a bridge on Ink was wrong, and I spent an evening thinking "that is just how L2s work". It was not. The default read is now both lists. EVM Received/Spent get labelled as a recent window, because those account lists are paginated. I will not pretend they are Bitcoin lifetime totals. mempool.space actually has those.

Then the production stuff. Throttle per chain. Cache. Only walk the graph someone clicked. A 429 gets a retry, then a notice that names the explorer (not "upstream error"), and the node stays clickable. I would rather show a hole than a graphic that quietly dropped half the counterparties. People notice holes. They do not notice a too perfect tree.

I keep talking myself out of decorating nodes. Blockscout has labels, decoded methods, token holders. They are off the first version. Once you have a ranked list, naming things feels like work. It is also how you start writing a biography. First version has to be something a sceptic can re check. The extra fields are still there when I am ready to put a source on them.

Reliability has been the usual public API deal. Stay under the published RPS, handle empty pages, do not burst because a busy address got pasted. I have not sat around blaming Blockscout for downtime. Running my own node would have been a different kind of downtime, and I would have been the one waking up for it.

## How are people using it? What do they actually ask?

Nobody asks for calldata.

They ask treasurer questions. Who funded this. Who got paid. What is still there. A `bc1...` is Bitcoin, mempool.space. A `0x...` needs the chain picker (same string, two ledgers) and then Blockscout.

If they publish, a project is one wallet on one chain. That is on purpose and it annoys people who wanted to "just edit the address later". Binding is fixed. Share the page or the tag, donor scans a QR, the trail moves when the watcher sees what the explorer already saw.

Then they click a hop. Or they open the explorer and read the raw tx. Bitcoin: mempool.space. Ethereum and Ink: Blockscout. If those two views disagree, I am wrong. I still click through after a deploy. Habit from shipping a wrong Ink total once.

The questions are ordinary. "Where did this donation go?" "Did that payment land?" "What is unspent?" On EVM that is the Blockscout account module. On Bitcoin it is Esplora address stats and txs. Users never see either. They just need the explorer still to be there when they decide I am full of it for a minute.

## What's next? More data sources, or more Blockscout?

More Blockscout on EVM. Bitcoin stays on mempool.space. I am not looking for a third EVM brain.

Adding a chain should stay boring. Next EVM network is `apiBase` plus a chain ID. That is why the unified API matters. One client, as many EVM ledgers as they index. Solana is a different adapter. Later, if ever. A Bitcoin change is an Esplora change.

The list I keep reordering:

1. **`tokentx`.** A lot of treasuries hold USDC, not only ETH. The page is native honest today. Token honest is next, still just facts.
2. **Address metadata, with a source.** A Blockscout tag on a known contract is better than a bare `0x`. It stays a chip. It does not become "I know who this is".
3. **Decoded calls in the history list.** "Swap" or "bridge deposit" next to the explorer link. Not as a verdict on a node in the tree. I do not trust myself with that.

If the trail needs another fact, it comes from Blockscout or it stays off the page.

## How can people get started?

The site: [wherecoinsgo.org](https://wherecoinsgo.org). Paste Bitcoin for the mempool.space path. Paste Ethereum or Ink and click through to Blockscout. Make an account when you want your own project. Free is one Bitcoin project. Pro is tags, deeper provenance, more chains. Yes, free is Bitcoin only. That is the product, not a docs typo.

The EVM API: a key at [dev.blockscout.com](https://dev.blockscout.com). Ethereum is `eth.blockscout.com`. Ink is chain ID `57073` on the unified API, explorer is `explorer.inkonchain.com`. `balance`, `txlist`, `txlistinternal` is enough to build a trail on any chain they host. Bitcoin equivalent is public Esplora on [mempool.space](https://mempool.space).

The rest is layout, and not adding a story the explorer did not tell.

wherecoinsgo.org is a solo project by [Juraj Kosik](https://github.com/jkosik).
