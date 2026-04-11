import { Link } from 'react-router-dom';
import './Header.css';

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner page-container">
        <Link to="/" className="wordmark">
          <span className="wordmark-re">Re</span>
          <span className="wordmark-motion">Motion</span>
        </Link>
        <p className="header-tagline">Sport Mobility Analyzer</p>
      </div>
    </header>
  );
}
