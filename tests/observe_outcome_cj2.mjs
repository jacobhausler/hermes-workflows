// Offline NodePanel harness. The actual plugin is unchanged except import shims and visibility.
import assert from 'node:assert/strict'
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
const [source, dir, cases] = process.argv.slice(2)
const write = (name, src) => writeFileSync(join(dir, name + '.mjs'), src)
globalThis.calls = []
write('sdk', `
export function atom(value) { return {get:()=>value,set:v=>{value=v}} }
export const Badge='Badge', Button='button', cn=(...x)=>x.join(' '), Codicon='Codicon',
 COMPOSER_AREAS={}, EmptyState='EmptyState', PANES_AREA='panes', PanelListRow='PanelListRow',
 PanelPill='PanelPill', PanelSectionLabel='PanelSectionLabel', ROUTES_AREA='routes',
 ScrollArea='ScrollArea', StatusDot='StatusDot', TRANSCRIPT_DIRECTIVE_AREA='directive'
const track = name => (...args) => { globalThis.calls.push([name,...args]) }
export const host={openSession:track('openSession'),navigate:track('navigate'),notify:track('notify'),
 composer:{insertText:track('insertText'),submit:track('submit')},
 state:{focusedSessionId:atom(''),focusedStoredSessionId:atom('')}}
export const useValue=x=>x.get(), useQuery=()=>({}), useMutation=()=>({mutate:track('mutate')}),
 useQueryClient=()=>({invalidateQueries:track('invalidateQueries')})
`)
write('react', `
export const useEffect=()=>{}, useId=()=> 'witness', useRef=()=>({current:null}),
 useState=x=>[typeof x==='function'?x():x,()=>{}]
`)
write('jsx', `export const jsx=(type,props)=>({type,props}),jsxs=jsx,Fragment='fragment'`)
write('product', readFileSync(source,'utf8').replace("'@hermes/plugin-sdk'", "'./sdk.mjs'")
 .replace("'react'", "'./react.mjs'").replace("'react/jsx-runtime'", "'./jsx.mjs'") + '\nexport { NodePanel, $fanItem }\n')
const { NodePanel, $selNode, $fanItem, markNavFocus } = await import(join(dir,'product.mjs'))
const material = n => !n || typeof n!=='object' ? n : Array.isArray(n) ? n.map(material)
 : typeof n.type==='function' ? material(n.type(n.props))
 : {...n,props:{...n.props,children:material(n.props?.children)}}
const walk = function* (n) {
 if (!n || typeof n!=='object') return
 if (Array.isArray(n)) { for (const i of n) yield* walk(i); return }
 yield n
 yield* walk(n.props?.children)
}
const text = n => Array.isArray(n)?n.map(text).join(' '):typeof n==='string'?n:textMaybe(n?.props?.children)
const textMaybe = n => n==null?'':text(n)
const failures=[]
for (const {name,view,node,index,allowed} of JSON.parse(readFileSync(cases,'utf8'))) {
 const show=()=>material(NodePanel({detail:view}))
 const list=t=>[...walk(t)].filter(n=>n.type==='button').map(n=>n.props)
 $selNode.set({runId:view.id,nodeId:node}); $fanItem.set(null); markNavFocus(null); calls.length=0
 const tones = {good:'done', bad:'failed', muted:'pending'}
 const chips=list(show()).filter(p=>Array.isArray(p.children) && p.children[0]?.type==='StatusDot')
 const target=chips[index]
 assert.ok(target, `${name}: no selectable status-bearing chip at index ${index}`)
 const painted=text(target.children[1]).trim()
 const tone=target.children[0].props.tone
 const outcome=tones[tone]
 assert.ok(outcome, `${name}: unknown exposed StatusDot tone ${tone}`)
 target.onClick({stopPropagation(){}})
 assert.deepEqual($fanItem.get(), {runId:view.id,nodeId:node,index}, name)
 const tree=show()
 const link=list(tree).find(p=>p.children==='open recorded chat')
 if (link) await link.onClick()
 const actual={painted,outcome,unavailable:text(tree).includes('Session unavailable'),calls:[...calls]}
 console.log(JSON.stringify({name,...actual}))

 try { assert.ok(allowed.some(x=>JSON.stringify(x)===JSON.stringify(actual)),JSON.stringify({name,allowed,actual})) }
 catch (e) { failures.push(e.message) }
}
if (failures.length) { console.error(failures.join('\n')); process.exitCode=1 }
