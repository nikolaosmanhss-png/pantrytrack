# Problem Statement

## Context

Independent cafés, tavernas and bakeries work with perishable stock, small margins and very little administrative time. In most of them stock is tracked on paper, in a notebook next to the fridge, or in an informal spreadsheet.

## The problem

1. **Stock-outs** – an ingredient runs out during service because nobody noticed it was low. Dishes are removed from the menu and customers are disappointed.
2. **Food waste** – to avoid stock-outs, owners over-order. Perishable products (dairy, fresh produce, meat) then expire and are thrown away. Nobody knows how much money this costs per month.
3. **No data for decisions** – without records it is impossible to see which products are wasted most, which supplier to order from, or how much stock is worth.

## Why existing solutions do not fit

Commercial inventory platforms exist, but they are typically sold as monthly subscriptions, are built for multi-site chains and require training and integration with a POS system. For a single small business the cost and complexity are often higher than the benefit.

## Target users

- Owner or manager of a small food business (1–20 staff).
- Kitchen staff who record usage and waste.
- Developers who want a simple base to build their own stock tool.

## Requirements (v0.1)

| ID | Requirement | Status |
|---|---|---|
| R1 | Add items with unit, category, cost, supplier and re-order level | Done |
| R2 | Import items from CSV | Done |
| R3 | Record deliveries, usage and waste with reason | Done |
| R4 | Prevent stock from going negative | Done |
| R5 | Show low-stock items | Done |
| R6 | Suggest an order list grouped by supplier | Done |
| R7 | Report usage, waste cost and waste rate per item | Done |
| R8 | Produce a chart of the most wasted items | Done |
| R9 | Work offline with no server | Done |
| R10 | Expiry dates per batch (FIFO) | Planned |

## Why open source?

The problem is shared by thousands of small businesses but none of them can justify building custom software alone. An open-source tool lets the community share the cost: one business adds a translation, another a feature, a student fixes a bug. The owner keeps full control of their data and is not locked into a vendor.
