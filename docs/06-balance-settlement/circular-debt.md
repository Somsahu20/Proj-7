# Circular Debt Resolution

## Overview

Circular debts occur when A owes B, B owes C, and C owes A. The system detects and resolves these cycles to simplify settlements.

---

## Circular Debt Detection

### What is Circular Debt?

```
A owes B: $50
B owes C: $30
C owes A: $20

This forms a cycle: A → B → C → A
```

### Detection Algorithm

```python
def find_cycles(debts: dict[tuple, Decimal]) -> list[Cycle]:
    """
    Uses DFS to find all cycles in the debt graph.
    """
    graph = build_graph(debts)
    cycles = []

    for node in graph:
        visited = set()
        stack = [(node, [node])]

        while stack:
            current, path = stack.pop()
            for neighbor in graph[current]:
                if neighbor == node and len(path) > 2:
                    cycles.append(path + [neighbor])
                elif neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))

    return deduplicate_cycles(cycles)
```

---

## Cycle Resolution

### Resolution Strategy

For a cycle, find the minimum debt and subtract from all debts in the cycle:

```
Original:
A → B: $50
B → C: $30
C → A: $20

Minimum in cycle: $20

After resolution:
A → B: $50 - $20 = $30
B → C: $30 - $20 = $10
C → A: $20 - $20 = $0 (eliminated)

Result: 2 transactions instead of 3
```

### Algorithm

```python
def resolve_cycle(cycle: list, debts: dict) -> dict:
    """
    Resolve a single cycle by subtracting minimum debt.
    """
    # Find minimum debt in cycle
    min_debt = min(
        debts[(cycle[i], cycle[i+1])]
        for i in range(len(cycle) - 1)
    )

    # Subtract from all edges in cycle
    for i in range(len(cycle) - 1):
        edge = (cycle[i], cycle[i+1])
        debts[edge] -= min_debt
        if debts[edge] == 0:
            del debts[edge]

    return debts
```

---

## API Endpoints

### Detect Cycles

**Request**
```
GET /api/v1/groups/{group_id}/balances/cycles
Authorization: Bearer <access_token>
```

**Response**
```json
HTTP 200 OK
{
  "has_cycles": true,
  "cycles": [
    {
      "participants": ["Alice", "Bob", "Carol"],
      "debts": [
        {"from": "Alice", "to": "Bob", "amount": 50.00},
        {"from": "Bob", "to": "Carol", "amount": 30.00},
        {"from": "Carol", "to": "Alice", "amount": 20.00}
      ],
      "min_reducible": 20.00
    }
  ],
  "potential_savings": {
    "transactions_before": 3,
    "transactions_after": 2,
    "reduction": 1
  }
}
```

### Resolve Cycles

**Request**
```
POST /api/v1/groups/{group_id}/balances/resolve-cycles
Authorization: Bearer <access_token>
```

Note: This doesn't actually change balances - it returns what the simplified structure would look like. Actual balance changes only happen through confirmed payments.

**Response**
```json
HTTP 200 OK
{
  "resolved_debts": [
    {"from": "Alice", "to": "Bob", "amount": 30.00},
    {"from": "Bob", "to": "Carol", "amount": 10.00}
  ],
  "eliminated": [
    {"from": "Carol", "to": "Alice", "amount": 20.00, "reason": "cycle_resolved"}
  ],
  "net_effect": "Carol no longer needs to pay Alice. Bob pays Carol less."
}
```

---

## Visualization

### Debt Graph Before

```
       $50
   A ────────▶ B
   ▲           │
   │           │ $30
   │$20        │
   │           ▼
   └────────── C
```

### Debt Graph After Resolution

```
       $30
   A ────────▶ B
               │
               │ $10
               │
               ▼
               C
```

---

## Complex Cycles

### Multiple Overlapping Cycles

```
A → B: $100
B → C: $60
C → A: $40
B → D: $30
D → A: $20

Cycles:
1. A → B → C → A (min: $40)
2. A → B → D → A (min: $20)
```

### Resolution Order
1. Resolve smallest cycle first
2. Recalculate remaining cycles
3. Continue until no cycles remain

---

## User Interface

### Cycle Notification

When cycles are detected:
- Badge on "Balances" tab
- Explanation of what cycles mean
- "Simplify" button to view resolution

### Cycle Explanation
```
💡 We found a circular debt!

Alice owes Bob, Bob owes Carol, and Carol owes Alice.
This can be simplified:

Instead of:
  Alice → Bob: $50
  Bob → Carol: $30
  Carol → Alice: $20

After simplification:
  Alice → Bob: $30
  Bob → Carol: $10

Carol doesn't need to pay anyone!
```

---

## Edge Cases

### Self-Cycles
```
A → A: $0 (not possible by design)
```

### Two-Person Cycle
```
A → B: $50
B → A: $30

Resolution:
A → B: $20 (net difference)
```

### No Cycles
```
A → B: $50
A → C: $30
B → C: $20

No cycles exist. Standard simplification applies.
```

---

## Integration with Simplification

Cycle resolution is part of the debt simplification pipeline:

```
1. Calculate net balances
2. Detect cycles
3. Resolve cycles
4. Apply minimum cash flow algorithm
5. Return optimized settlements
```

---

## Acceptance Criteria

### Detection
- [ ] Correctly identifies cycles
- [ ] Handles multiple cycles
- [ ] Handles overlapping cycles
- [ ] Returns no cycles when none exist

### Resolution
- [ ] Correctly calculates minimum debt
- [ ] Subtracts from all cycle edges
- [ ] Eliminates zero-value debts
- [ ] Preserves total debt amounts

### API
- [ ] Detection endpoint works
- [ ] Resolution endpoint shows preview
- [ ] Integrates with simplification

### UI
- [ ] Cycle notification displayed
- [ ] Clear explanation provided
- [ ] Simplify action available
