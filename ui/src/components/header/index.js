import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Navbar, NavbarBrand, Button } from 'reactstrap';
import { apiPost } from '../../actions/api';
import history from '../../history';
import { LOGOUT_URL } from '../../api/Navigation';
import { TOKEN_KEY } from '../../constants/constants';
import './Header.css';


class Header extends React.Component {
  constructor(props) {
    super(props);

    this.handleLogout = this.handleLogout.bind(this);
    this.handleLogoutSuccess = this.handleLogoutSuccess.bind(this);
    this.renderLogoutButton = this.renderLogoutButton.bind(this);
  }

  handleLogout() {
    this.props.apiPost(
      LOGOUT_URL,
      null,
      this.handleLogoutSuccess,
      null
    );
  }

  handleLogoutSuccess() {
    localStorage.removeItem(TOKEN_KEY);

    history.push('/login');
  }

  renderLogoutButton() {
    const token = localStorage.getItem(TOKEN_KEY);

    return token && (
      <Button
        color="secondary"
        onClick={this.handleLogout}
      >
        Выйти
      </Button>
    );
  }

  render() {
    return (
      <Navbar
        className="header"
        color="faded"
        light
      >
        <NavbarBrand href="/">
          TezAviaSchedule
        </NavbarBrand>
        {
          this.renderLogoutButton()
        }
      </Navbar>
    );
  }
}

const mapDispatchToProps = dispatch => bindActionCreators({
  apiPost,
}, dispatch);

export default connect(null, mapDispatchToProps)(Header);
