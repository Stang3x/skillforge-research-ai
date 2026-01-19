# Mermaid Diagram Syntax Reference

Complete syntax guide for generating diagrams with Mermaid.

## Supported Diagram Types

| Type | Use Case |
|------|----------|
| Flowchart | Process flows, decision trees, workflows |
| Sequence | API calls, system interactions, message flows |
| Class | OOP architecture, data models |
| State | State machines, lifecycle diagrams |
| Mindmap | Concept maps, brainstorming, hierarchies |
| Gantt | Project timelines, schedules |
| Pie | Data distribution |
| Git Graph | Branch visualization |
| ER Diagram | Database schemas |
| User Journey | Experience mapping |

---

## 1. Flowchart

### Direction
```mermaid
flowchart LR   %% Left to Right
flowchart TD   %% Top Down (default)
flowchart BT   %% Bottom to Top
flowchart RL   %% Right to Left
```

### Node Shapes
```mermaid
flowchart LR
    A[Rectangle]
    B(Rounded)
    C([Stadium])
    D[[Subroutine]]
    E[(Database)]
    F((Circle))
    G{Diamond}
    H{{Hexagon}}
    I>Asymmetric]
```

### Arrows/Links
```mermaid
flowchart LR
    A --> B           %% Arrow
    A --- B           %% Line
    A -.-> B          %% Dotted arrow
    A ==> B           %% Thick arrow
    A --o B           %% Circle end
    A --x B           %% Cross end
    A <--> B          %% Bidirectional
    A -->|label| B    %% With label
```

### Subgraphs
```mermaid
flowchart TB
    subgraph Group1[Title]
        A --> B
    end
    subgraph Group2
        C --> D
    end
    B --> C
```

### Styling
```mermaid
flowchart LR
    A:::highlight --> B
    classDef highlight fill:#ff0,stroke:#333
    style A fill:#f9f,stroke:#333,stroke-width:4px
```

---

## 2. Sequence Diagram

### Basic
```mermaid
sequenceDiagram
    participant A as Client
    participant B as Server
    participant C as Database

    A->>B: Request
    B->>C: Query
    C-->>B: Results
    B-->>A: Response
```

### Arrow Types
| Syntax | Description |
|--------|-------------|
| `->` | Solid line |
| `-->` | Dotted line |
| `->>` | Solid with arrow |
| `-->>` | Dotted with arrow |
| `-x` | Solid with cross |
| `--x` | Dotted with cross |
| `-)` | Async (open arrow) |

### Activations
```mermaid
sequenceDiagram
    A->>+B: Request
    B->>+C: Query
    C-->>-B: Result
    B-->>-A: Response
```

### Loops & Conditions
```mermaid
sequenceDiagram
    loop Every minute
        A->>B: Heartbeat
    end

    alt Success
        B-->>A: OK
    else Failure
        B-->>A: Error
    end

    opt Optional
        A->>B: Extra call
    end
```

### Notes
```mermaid
sequenceDiagram
    A->>B: Message
    Note right of B: Processing...
    Note over A,B: Shared note
```

### Parallel
```mermaid
sequenceDiagram
    par Task 1
        A->>B: Request 1
    and Task 2
        A->>C: Request 2
    end
```

---

## 3. Class Diagram

### Classes & Members
```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +eat() void
        +sleep() void
    }

    class Dog {
        +String breed
        +bark() void
    }
```

### Visibility
| Prefix | Meaning |
|--------|---------|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package |

### Relationships
```mermaid
classDiagram
    Animal <|-- Dog        %% Inheritance
    Car *-- Engine         %% Composition
    Library o-- Book       %% Aggregation
    Student --> Course     %% Association
    Class1 ..> Class2      %% Dependency
    Interface ..|> Class   %% Realization
```

### Cardinality
```mermaid
classDiagram
    Company "1" --> "*" Employee : employs
    Order "1" --> "1..*" LineItem : contains
```

### Annotations
```mermaid
classDiagram
    class Shape {
        <<abstract>>
        +draw()
    }
    class IPayable {
        <<interface>>
        +pay()
    }
    class Color {
        <<enumeration>>
        RED
        GREEN
        BLUE
    }
```

---

## 4. State Diagram

### Basic
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: start
    Processing --> Complete: done
    Processing --> Error: fail
    Complete --> [*]
    Error --> Idle: retry
```

### Composite States
```mermaid
stateDiagram-v2
    [*] --> Active
    state Active {
        [*] --> Running
        Running --> Paused: pause
        Paused --> Running: resume
    }
    Active --> [*]: stop
```

### Fork/Join
```mermaid
stateDiagram-v2
    state fork_state <<fork>>
    state join_state <<join>>

    [*] --> fork_state
    fork_state --> State1
    fork_state --> State2
    State1 --> join_state
    State2 --> join_state
    join_state --> [*]
```

### Choice
```mermaid
stateDiagram-v2
    state check <<choice>>
    [*] --> check
    check --> Valid: if valid
    check --> Invalid: if invalid
```

### Notes
```mermaid
stateDiagram-v2
    State1: Active
    note right of State1
        Important note
    end note
```

---

## 5. Mindmap

### Basic Structure (indentation-based)
```mermaid
mindmap
    root((Central Topic))
        Branch1
            Leaf1
            Leaf2
        Branch2
            Leaf3
                SubLeaf1
        Branch3
```

### Node Shapes
```mermaid
mindmap
    root[Square Root]
        (Rounded)
        ((Circle))
        ))Cloud((
        {{Hexagon}}
```

### Icons
```mermaid
mindmap
    root((Project))
        Planning::icon(fa fa-calendar)
        Development::icon(fa fa-code)
        Testing::icon(fa fa-bug)
```

---

## 6. Pie Chart

```mermaid
pie title Distribution
    "Category A" : 40
    "Category B" : 30
    "Category C" : 20
    "Category D" : 10
```

---

## 7. Gantt Chart

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD

    section Phase 1
    Task 1           :a1, 2024-01-01, 30d
    Task 2           :after a1, 20d

    section Phase 2
    Task 3           :2024-02-15, 25d
    Milestone        :milestone, m1, 2024-03-15, 0d
```

---

## 8. ER Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "ordered in"

    CUSTOMER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        date created
        int customer_id FK
    }
```

---

## 9. Git Graph

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
```

---

## Common Styling

### Theme Configuration
```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
    A --> B
```

Available themes: `default`, `dark`, `forest`, `neutral`, `base`

### Custom Colors
```mermaid
flowchart LR
    A --> B
    style A fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#4ecdc4,stroke:#333,stroke-width:2px
```

### Class Definitions
```mermaid
flowchart LR
    A:::red --> B:::blue
    classDef red fill:#ff6b6b,stroke:#333
    classDef blue fill:#4ecdc4,stroke:#333
```

---

## Usage in Python

### Generate Mermaid Code
```python
def generate_flowchart(nodes, edges):
    """Generate Mermaid flowchart from nodes and edges"""
    lines = ["flowchart TD"]

    for node_id, label in nodes.items():
        lines.append(f"    {node_id}[{label}]")

    for source, target, label in edges:
        if label:
            lines.append(f"    {source} -->|{label}| {target}")
        else:
            lines.append(f"    {source} --> {target}")

    return "\n".join(lines)
```

### Render Options
1. **Mermaid Live Editor**: https://mermaid.live
2. **GitHub/GitLab**: Native rendering in markdown
3. **HTML**: Include mermaid.js library
4. **Python**: Use `mermaid-py` or save as `.mmd` file

---

## Agent Workflow Example

```mermaid
flowchart TD
    subgraph Input
        U[User Query]
    end

    subgraph Coordinator
        C{Analyze Complexity}
    end

    subgraph Agents
        R[Researcher]
        A[Analyst]
        W[Writer]
    end

    subgraph Output
        O[Final Report]
    end

    U --> C
    C -->|Simple| W
    C -->|Moderate| R --> W
    C -->|Complex| R --> A --> W
    W --> O

    style C fill:#4a90d9,stroke:#333
    style R fill:#50c878,stroke:#333
    style A fill:#da70d6,stroke:#333
    style W fill:#20b2aa,stroke:#333
```

---

## Multi-Agent System Example

```mermaid
sequenceDiagram
    participant U as User
    participant C as Coordinator
    participant R as Researcher
    participant A as Analyst
    participant W as Writer

    U->>C: Complex Query
    C->>C: Create Plan
    C->>R: Research Task

    activate R
    R->>R: Search arXiv
    R->>R: Search GitHub
    R->>R: Analyze PDFs
    R-->>C: Findings
    deactivate R

    C->>A: Analyze Findings
    activate A
    A->>A: Identify Patterns
    A->>A: Draw Conclusions
    A-->>C: Analysis
    deactivate A

    C->>W: Write Report
    activate W
    W->>W: Format Content
    W-->>C: Report
    deactivate W

    C-->>U: Final Response
```

---

## References

- Official Docs: https://mermaid.js.org
- Live Editor: https://mermaid.live
- GitHub Repo: https://github.com/mermaid-js/mermaid
