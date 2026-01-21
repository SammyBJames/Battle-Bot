tailwind.config = {
    darkMode: 'media',
    theme: {
        extend: {
            colors: {
                background: "light-dark(hsl(0 0% 100%), hsl(240 10% 3.9%))", 
                foreground: "light-dark(hsl(240 10% 3.9%), hsl(0 0% 98%))",
                card: {
                    DEFAULT: "light-dark(hsl(0 0% 100%), hsl(240 10% 3.9%))", 
                    foreground: "light-dark(hsl(240 10% 3.9%), hsl(0 0% 98%))",
                },
                popover: {
                    DEFAULT: "light-dark(hsl(0 0% 100%), hsl(240 10% 3.9%))",
                    foreground: "light-dark(hsl(240 10% 3.9%), hsl(0 0% 98%))",
                },
                primary: {
                    DEFAULT: "light-dark(hsl(240 5.9% 10%), hsl(0 0% 98%))", 
                    foreground: "light-dark(hsl(0 0% 98%), hsl(240 5.9% 10%))",
                },
                secondary: {
                    DEFAULT: "light-dark(hsl(240 4.8% 95.9%), hsl(240 3.7% 15.9%))", 
                    foreground: "light-dark(hsl(240 5.9% 10%), hsl(0 0% 98%))",
                },
                muted: {
                    DEFAULT: "light-dark(hsl(240 4.8% 95.9%), hsl(240 3.7% 15.9%))", 
                    foreground: "light-dark(hsl(240 3.8% 46.1%), hsl(240 5% 64.9%))",
                },
                accent: {
                    DEFAULT: "light-dark(hsl(240 4.8% 95.9%), hsl(240 3.7% 15.9%))", 
                    foreground: "light-dark(hsl(240 5.9% 10%), hsl(0 0% 98%))",
                },
                destructive: {
                    DEFAULT: "light-dark(hsl(0 84.2% 60.2%), hsl(0 62.8% 30.6%))", 
                    foreground: "light-dark(hsl(0 0% 98%), hsl(0 0% 98%))",
                },
                border: "light-dark(hsl(240 5.9% 90%), hsl(240 3.7% 15.9%))",
                input: "light-dark(hsl(240 5.9% 90%), hsl(240 3.7% 15.9%))",
                ring: "light-dark(hsl(240 5.9% 10%), hsl(240 4.9% 83.9%))",
            },
            borderRadius: {
                lg: '0.5rem',
                md: 'calc(0.5rem - 2px)',
                sm: 'calc(0.5rem - 4px)',
            },
        },
    },
}
