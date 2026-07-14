/**
 * Search Parser Composable
 * Implements an advanced boolean search parser (AND, OR, NOT, Groups, Exact Phrase, Fields)
 */

export function filterModelsByQuery(models, query) {
  if (!query || !query.trim()) return models;
  
  const tokens = tokenize(query);
  const ast = parse(tokens);
  
  return models.filter(model => evaluate(ast, model));
}

function tokenize(query) {
    const tokens = [];
    const regex = /(<)|(>)|(\|)|(!|-)|([a-zA-Z0-9_]+:"[^"]+")|([a-zA-Z0-9_]+:[^\s<>|!]+)|("[^"]+")|([^\s<>|!]+)/g;
    
    let match;
    while ((match = regex.exec(query)) !== null) {
        const raw = match[0];
        if (raw === '<') tokens.push({ type: 'GROUP_START' });
        else if (raw === '>') tokens.push({ type: 'GROUP_END' });
        else if (raw === '|') tokens.push({ type: 'OR' });
        else if (raw === '!' || raw === '-') tokens.push({ type: 'NOT' });
        else if (raw.includes(':') && !raw.startsWith('"')) {
            const colonIdx = raw.indexOf(':');
            const field = raw.substring(0, colonIdx).toLowerCase();
            let value = raw.substring(colonIdx + 1);
            if (value.startsWith('"') && value.endsWith('"')) {
                value = value.substring(1, value.length - 1);
            }
            tokens.push({ type: 'FIELD_MATCH', field, value: value.toLowerCase() });
        } else {
            let value = raw;
            if (value.startsWith('"') && value.endsWith('"')) {
                value = value.substring(1, value.length - 1);
            }
            tokens.push({ type: 'MATCH', value: value.toLowerCase() });
        }
    }
    return tokens;
}

function parse(tokens) {
    let current = 0;

    function walk() {
        if (current >= tokens.length) return null;
        return parseOr();
    }

    function parseOr() {
        let left = parseAnd();
        
        while (current < tokens.length && tokens[current].type === 'OR') {
            current++;
            let right = parseAnd();
            left = { type: 'OR_EXPR', left, right };
        }
        return left;
    }

    function parseAnd() {
        let nodes = [];
        let node = parseUnary();
        if (node) nodes.push(node);

        // Implicit AND (space) is essentially adjacent expressions not separated by OR or GROUP_END
        while (current < tokens.length && tokens[current].type !== 'OR' && tokens[current].type !== 'GROUP_END') {
            let nextNode = parseUnary();
            if (nextNode) {
                nodes.push(nextNode);
            }
        }
        
        if (nodes.length === 1) return nodes[0];
        if (nodes.length === 0) return null;
        return { type: 'AND_EXPR', nodes };
    }

    function parseUnary() {
        if (current >= tokens.length) return null;
        
        if (tokens[current].type === 'NOT') {
            current++;
            let expr = parseUnary();
            return { type: 'NOT_EXPR', expr };
        }
        
        return parsePrimary();
    }

    function parsePrimary() {
        if (current >= tokens.length) return null;
        let token = tokens[current];

        if (token.type === 'GROUP_START') {
            current++;
            let expr = parseOr();
            if (current < tokens.length && tokens[current].type === 'GROUP_END') {
                current++;
            }
            return expr;
        }

        if (token.type === 'MATCH' || token.type === 'FIELD_MATCH') {
            current++;
            return token;
        }

        current++;
        return null;
    }

    return walk();
}

function evaluate(ast, model) {
    if (!ast) return true;

    if (ast.type === 'OR_EXPR') {
        return evaluate(ast.left, model) || evaluate(ast.right, model);
    }
    if (ast.type === 'AND_EXPR') {
        for (let node of ast.nodes) {
            if (!evaluate(node, model)) return false;
        }
        return true;
    }
    if (ast.type === 'NOT_EXPR') {
        return !evaluate(ast.expr, model);
    }
    
    // Searchable text for global match (no field specified)
    const searchableText = `${model.name || ''} ${model.filename || ''} ${model.tags || ''} ${model.category || ''} ${model.description || ''} ${model.baseModel || ''} ${model.sdVersion || ''} ${model.creator || ''} ${model.folder || ''} ${model.civitaiName || ''} ${model.civitaiUrl || ''}`.toLowerCase();

    if (ast.type === 'MATCH') {
        return searchableText.includes(ast.value);
    }

    if (ast.type === 'FIELD_MATCH') {
        let fieldText = "";
        switch (ast.field) {
            case 'base': case 'sdversion': case 'basemodel':
                fieldText = `${model.sdVersion || ''} ${model.baseModel || ''}`.toLowerCase();
                break;
            case 'url': case 'link': case 'civitaiurl':
                fieldText = (model.civitaiUrl || '').toLowerCase();
                break;
            case 'cat': case 'category':
                fieldText = (model.category || '').toLowerCase();
                break;
            case 'tag': case 'tags':
                fieldText = (model.tags || '').toLowerCase();
                break;
            case 'auth': case 'author': case 'creator':
                fieldText = (model.creator || '').toLowerCase();
                break;
            case 'name':
                fieldText = (model.name || '').toLowerCase();
                break;
            case 'file': case 'filename':
                fieldText = (model.filename || '').toLowerCase();
                break;
            case 'folder':
                fieldText = (model.folder || '').toLowerCase();
                break;
            case 'civitai': case 'civitainame':
                fieldText = (model.civitaiName || '').toLowerCase();
                break;
            case 'desc': case 'description':
                fieldText = (model.description || '').toLowerCase();
                break;
            default:
                return true; 
        }
        return fieldText.includes(ast.value);
    }

    return true;
}
