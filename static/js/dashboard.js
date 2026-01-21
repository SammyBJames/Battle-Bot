document.addEventListener('DOMContentLoaded', () => {
    function renderTable(data) {
        const container = document.getElementById('results-container');
        const tbody = document.getElementById('results-body');
        
        if (!container || !tbody) return;
        
        tbody.innerHTML = '';
        
        // No results
        if (data.length == 0) {
            container.classList.remove('hidden');
            tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-muted-foreground">No results found.</td></tr>`;
            return;
        }

        // Some results
        container.classList.remove('hidden');
        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted';
            tr.innerHTML = `
                <td class="p-4 align-middle">${row.id}</td>
                <td class="p-4 align-middle">${row.name}</td>
                <td class="p-4 align-middle">${row.description}</td>
                <td class="p-4 align-middle">${row.category}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function setupSearch() {
        const searchForm = document.getElementById('search-form');
        if (!searchForm) return;

        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = searchForm.q.value;
            
            try {
                const response = await fetch(searchForm.action, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ q: query })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    renderTable(data);
                    return;
                }
            }
            // Otherwise something went wrong
            catch (err) { console.error(err); }
            const container = document.getElementById('results-container');
            const tbody = document.getElementById('results-body');
            
            if (container && tbody) {
                container.classList.remove('hidden');
                tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-destructive font-medium">Something went wrong.</td></tr>`;
            }
        });
    }
    
    function setupRobotControls() {

        document.querySelectorAll('.robot-controls form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const direction = form.direction.value;

                try {
                    const response = await fetch(form.action, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ direction: direction })
                    });

                    const data = await response.json();
                    const logContainer = document.getElementById('robot-log');
                    const entry = document.createElement('div');
                    const timestamp = new Date().toLocaleTimeString();
                    const colorClass = data.status === 'success' ? 'text-green-500' : 'text-destructive';
                    
                    entry.className = 'flex justify-between items-start border-b border-border/50 pb-1 last:border-0';
                    entry.innerHTML = `
                        <span class="${colorClass}">${data.message}</span>
                        <span class="text-muted-foreground ml-2 text-[10px]">${timestamp}</span>
                    `;
                    
                    // Replace placeholder if it's the first entry
                    const firstChild = logContainer.firstElementChild;
                    if (firstChild && firstChild.classList.contains('italic')) {
                        logContainer.innerHTML = '';
                    }
                    
                    logContainer.prepend(entry);
                } catch (err) {
                    console.error('Error moving robot:', err);
                }
            });
        });
    }

    setupSearch();
    setupRobotControls();
});
