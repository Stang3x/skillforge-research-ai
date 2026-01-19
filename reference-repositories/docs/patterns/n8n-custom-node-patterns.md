# n8n Custom Node Patterns

This document captures patterns for developing custom n8n nodes, extracted from n8n-nodes-starter and community examples.

## Pattern: Basic Custom Node Structure

**Source**: [n8n-nodes-starter](../../references/n8n-nodes-starter/)

**Purpose**: Define the structure of a custom n8n node

**Context**: When you need to create a custom integration or operation not available in n8n's built-in nodes

**Implementation**:
```typescript
// Template - to be filled with actual examples from n8n-nodes-starter
import { INodeType, INodeTypeDescription } from 'n8n-workflow';

export class CustomNode implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Custom Node',
        name: 'customNode',
        group: ['transform'],
        version: 1,
        description: 'Description of what this node does',
        defaults: {
            name: 'Custom Node',
        },
        inputs: ['main'],
        outputs: ['main'],
        properties: [
            // Node parameters defined here
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        // Node logic here
    }
}
```

**Trade-offs**:
- **Pros**: Full control over node behavior, can integrate any API or service
- **Cons**: Requires TypeScript knowledge, must handle errors and edge cases

**Related Patterns**: API Integration Patterns for connecting to external services

---

## Pattern: Parameter Handling

**Source**: To be documented from n8n-nodes-starter

**Purpose**: Define and validate node parameters/inputs

**Context**: When your node needs user configuration (API keys, options, etc.)

**Implementation**:
```typescript
// Template - document parameter definition patterns from n8n examples
properties: [
    {
        displayName: 'Resource',
        name: 'resource',
        type: 'options',
        options: [
            { name: 'Option 1', value: 'option1' },
            { name: 'Option 2', value: 'option2' },
        ],
        default: 'option1',
    },
]
```

---

## Pattern: Credential Management

**Source**: To be documented from n8n-nodes-starter

**Purpose**: Handle API keys and credentials securely

**Context**: When your node needs to authenticate with external services

**Implementation**:
```typescript
// Template - document credential handling from n8n
credentials: [
    {
        name: 'customApi',
        required: true,
    },
]
```

---

## Pattern: Error Handling in Nodes

**Source**: To be documented

**Purpose**: Gracefully handle API errors and edge cases

**Context**: Making nodes robust and user-friendly

**Implementation**:
```typescript
// Template - document error handling best practices
try {
    // API call or operation
} catch (error) {
    // Proper error handling and user feedback
}
```

---

## Pattern: Pagination Handling

**Source**: To be documented

**Purpose**: Handle paginated API responses

**Context**: When APIs return data in pages/chunks

**Implementation**:
```typescript
// Template - document pagination patterns
// How to fetch all pages and return combined results
```

---

## Notes for Pattern Extraction

When documenting n8n node patterns:
1. **Structure** - How is the node class organized?
2. **Type Definitions** - What TypeScript types are used?
3. **Parameter Validation** - How are inputs validated?
4. **Error Messages** - How are errors communicated to users?
5. **Testing** - How are custom nodes tested?
6. **Documentation** - How should parameters be documented?
