import Notifications from './components/Notifications'
import ActivityFeed from './components/ActivityFeed'
import './App.css'

function App() {
    return (
        <div className="container">
            <header>
                <h1>React Server-Sent Events (SSE) Demo</h1>
                <p className="subtitle">Real-time updates without WebSockets</p>
            </header>

            <main className="grid">
                <Notifications />
                <ActivityFeed />
            </main>

            <footer>
                <p>Built with React & Express</p>
            </footer>
        </div>
    )
}

export default App
