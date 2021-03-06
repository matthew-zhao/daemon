import React from 'react';
import {
  Navbar,
  Nav,
  ButtonToolbar,
  ButtonGroup,
  Tooltip,
  OverlayTrigger,
  Button,
  Label,
  Glyphicon} from 'react-bootstrap';
import { remote } from 'electron';
import smalltalk from 'smalltalk';
import Ansible from '../utils/Ansible';
const storage = remote.require('electron-json-storage');

export default React.createClass({
  displayName: 'DNav',
  saveAddress(currentAddress) {
    let prompt = smalltalk.prompt(
      'Enter the IP address of the robot:',
      'Examples: 192.168.0.100, 127.0.0.1',
      currentAddress
    );
    prompt.then((value) => {
      storage.set('runtimeAddress', {
        address: value
      }, (err)=>{
        if (err) throw err;
        Ansible.reload();
      });
    }, ()=>console.log('Canceled'));
  },
  updateAddress() {
    storage.has('runtimeAddress').then((hasKey)=>{
      if (hasKey) {
        storage.get('runtimeAddress').then((data)=>{
          this.saveAddress(data.address);
        });
      } else {
        this.saveAddress('127.0.0.1');
      }
    });
  },
  getDawnVersion() {
    return process.env.npm_package_version;
  },
  render() {
    return (
      <Navbar fixedTop fluid>
        <Navbar.Header>
          <Navbar.Brand>
            {"Dawn v" +
              this.getDawnVersion() +
              (this.props.connection ? "" : " (disconnected)")}
          </Navbar.Brand>
          <Navbar.Toggle />
        </Navbar.Header>
        <Navbar.Collapse>
          <Navbar.Text>
            <Label bsStyle="success" id="battery-indicator">
              Battery Level: {
                this.props.connection ? this.props.battery : 'Not connected.'
              }
            </Label>
          </Navbar.Text>
          <Navbar.Form
            pullRight={true}>
            <ButtonToolbar>
              <ButtonGroup>
                <OverlayTrigger
                  placement="bottom"
                  overlay={
                    <Tooltip id={ 'tour-tooltip' }>
                      "Tour"
                    </Tooltip>
                  }>
                  <Button
                    bsStyle="info"
                    onClick={ this.props.startTour }
                    id="tour-button">
                    <Glyphicon glyph="info-sign" />
                  </Button>
                </OverlayTrigger>
                <OverlayTrigger
                  placement="bottom"
                  overlay={
                    <Tooltip id={ 'update-address-tooltip' }>
                      "Robot IP"
                    </Tooltip>
                  }>
                  <Button
                    bsStyle="info"
                    onClick={ this.updateAddress }
                    id = "update-address-button">
                    <Glyphicon glyph="transfer" />
                  </Button>
                </OverlayTrigger>
              </ButtonGroup>
            </ButtonToolbar>
          </Navbar.Form>
        </Navbar.Collapse>
      </Navbar>
    );
  }
});
