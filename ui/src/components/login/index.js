import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Container, Col, Row } from 'reactstrap';
import LoginFrom from '../form/LoginForm';
import { apiPost } from '../../actions/api';
import history from '../../history';
import { LOGIN_URL } from '../../api/Navigation';
import { TOKEN_KEY } from '../../constants/constants';


class LoginContainer extends React.Component {
  constructor(props) {
    super(props);

    this.handleLogin = this.handleLogin.bind(this);
    this.handleLoginSuccess = this.handleLoginSuccess.bind(this);
  }

  handleLogin(values) {
    this.props.apiPost(
      LOGIN_URL,
      values,
      this.handleLoginSuccess
    );
  }

  handleLoginSuccess(data) {
    const { token } = data;
    localStorage.setItem(TOKEN_KEY, token);

    history.push('/');
  }

  render() {
    return (
      <Container>
        <Row>
          <Col md={2} />
          <Col md={8}>
            <LoginFrom onSubmit={this.handleLogin} />
          </Col>
          <Col md={2} />
        </Row>
      </Container>
    );
  }
}

const mapDispatchToProps = dispatch => bindActionCreators({
  apiPost,
}, dispatch);

export default connect(null, mapDispatchToProps)(LoginContainer);
