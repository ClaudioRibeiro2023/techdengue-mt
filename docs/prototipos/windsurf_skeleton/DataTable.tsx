import React from 'react'

export const DataTable: React.FC<{ columns: string[], rows: (string | number)[][] }> = ({ columns, rows }) => {
  return (
    <div className="overflow-auto rounded-2xl border bg-white">
      <table className="w-full text-sm">
        <thead className="bg-slate-50">
          <tr>{columns.map(c => <th key={c} className="text-left p-2 font-medium">{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t">
              {r.map((v, j) => <td key={j} className="p-2">{String(v)}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
