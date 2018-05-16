import React from 'react';
import { Route, Redirect } from 'react-router-dom';

const TOKEN_KEY = 'token';


class PrivateRoute extends React.Component {
  constructor(props) {
    super(props);

    this.renderRoute = this.renderRoute.bind(this);
  }

  renderRoute(props) {
    const { component: Component } = this.props;
    const token = localStorage.getItem(TOKEN_KEY);

    if (!token) {
      return (
        <Redirect to={{
          pathname: '/login',
          state: { from: props.location }
        }}
        />
      );
    }

    return <Component {...props} />;
  }

  render() {
    // leave component, so that it won't be included into ...rest
    const { component: Component, ...rest } = this.props;

    return (
      <Route
        {...rest}
        render={this.renderRoute}
      />
    );
  }
}

export default PrivateRoute;
