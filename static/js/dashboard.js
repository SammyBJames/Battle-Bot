document.addEventListener('DOMContentLoaded', () => {
    // Search Handler
    const searchForm = document.getElementById('search-form');
    // Fallback if ID is not yet added, though we should add it.
    // Also handling the case where search might be disabled (not present in DOM)
    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(searchForm);
            const query = formData.get('q');
            
            try {
                // Send as JSON POST
                const response = await fetch(searchForm.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ q: query })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    renderTable(data);
                } else {
                    // Display generic error on the page
                    const container = document.getElementById('results-container');
                    const tbody = document.getElementById('results-body');
                    
                    if (container && tbody) {
                        container.classList.remove('hidden');
                        tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-destructive font-medium">Something went wrong.</td></tr>`;
                    }
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    function renderTable(data) {
        const container = document.getElementById('results-container');
        const tbody = document.getElementById('results-body');
        
        if (!container || !tbody) return;
        
        tbody.innerHTML = '';
        
        if (data.length > 0) {
            container.classList.remove('hidden');
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.className = "border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted";
                tr.innerHTML = `
                    <td class="p-4 align-middle">${row.id}</td>
                    <td class="p-4 align-middle">${row.name}</td>
                    <td class="p-4 align-middle">${row.description}</td>
                    <td class="p-4 align-middle">${row.category}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            container.classList.remove('hidden');
            tbody.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-muted-foreground">No results found.</td></tr>`;
        }
    }
    
    // Robot Move Handler
    document.querySelectorAll('form').forEach(form => {
        // Detect forms that go to the move handler
        const action = form.getAttribute('action');
        if (action && action.includes('/move')) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                // Get direction from data attribute or hidden input
                const formData = new FormData(form);
                const direction = formData.get('direction') || form.getAttribute('data-direction');

                try {
                    const response = await fetch(action, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ direction: direction })
                    });
                    const data = await response.json();
                     
                     const logContainer = document.getElementById('robot-log');
                     if (logContainer) {
                        const entry = document.createElement('div');
                        const timestamp = new Date().toLocaleTimeString();
                        const colorClass = data.status === 'success' ? 'text-green-500' : 'text-destructive';
                        
                        entry.className = "flex justify-between items-start border-b border-border/50 pb-1 last:border-0";
                        entry.innerHTML = `
                            <span class="${colorClass}">${data.message}</span>
                            <span class="text-muted-foreground ml-2 text-[10px]">${timestamp}</span>
                        `;
                        
                        // Check if it's the first real log replacing the placeholder
                        const firstChild = logContainer.firstElementChild;
                        if (firstChild && firstChild.classList.contains('italic')) {
                            logContainer.innerHTML = '';
                        }
                        
                        logContainer.prepend(entry);
                     }
                } catch (err) {
                    console.error("Error moving robot:", err);
                }
            });
        }
    });
});
