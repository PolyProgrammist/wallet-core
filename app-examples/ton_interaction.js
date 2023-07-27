
it("API TheOpenNetwork", () => {
    let your_api_key = <GET API KEY FROM https://t.me/tontestnetapibot for testnet and from https://t.me/tonapibot for mainnet >
 
    let testnet_base_url = 'https://testnet.toncenter.com/api';
    let mainnet_base_url = 'https://toncenter.com/api'
    let url_to_use = testnet_base_url;
    let base_url = url_to_use + '/v2';
    let index_base_url = url_to_use + '/index';
 
    function request(method, url, handle_response, data) {
      var req = new XMLHttpRequest();
      req.open(method, url);
      if (method == 'POST') {
        req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      }
      req.setRequestHeader("x-api-key", your_api_key);
      req.responseType = 'json';
      req.onload  = function() {
        var jsonResponse = req.response;
        handle_response(jsonResponse);
      };
      if (method == 'POST') {
        req.send(JSON.stringify(data));
      } else {
        req.send(null);
      }
    }
    
    request('GET', base_url + '/getAddressInformation?address=EQDTOhnuvYwNNZxpOHw--72oKKMGlcbLLl7cW_JimtfPyW1C', (response)=> {
      let balance = response['result']['balance'] / 1e9;
      console.log('Balance is: ', balance);
    }, {});
 
    request('GET', base_url + '/getWalletInformation?address=EQDTOhnuvYwNNZxpOHw--72oKKMGlcbLLl7cW_JimtfPyW1C', (response)=> {
      let seqno = response['result']['seqno'];
      console.log('Seqno is: ', seqno);
    }, {});
 
    function get_transaction_info(tx_hash) {
      let hash_encoded = encodeURIComponent(tx_hash);
      request('GET', index_base_url + '/getTransactionByHash?' + 'tx_hash=' + hash_encoded + '&include_msg_body=false', (response) => {
        response = response[0];
        let sender = '';
        let recipient = '';
        let value = 0;
        if ('out_msgs' in response && response['out_msgs'].length > 0) {
            sender = response['account'];
            let last_index = response['out_msgs'].length - 1;
            recipient = response['out_msgs'][last_index]['destination'];
            value = response['out_msgs'][last_index]['value'] / 1e9;
        } else {
            sender = response['in_msg']['source'];
            recipient = response['in_msg']['destination'];
            value = response['in_msg']['value'] / 1e9;
        }
  
        let unix_time = response['utime'];
        let fee = response['fee'] / 1e9;
        fee += (response['in_msg']['fwd_fee'] + response['in_msg']['ihr_fee']) / 1e9;
  
        console.log(value, sender, recipient, fee, unix_time);
      }, {});
    }
 
    get_transaction_info('ubGjEmeJEzzgfJAyJ8F4TjXuVr/0h1wfixw2Fu5HuN8=');
    get_transaction_info('ANGSu+5GlmW+vdrw6xVV88yz7NN4EXGg0TiEmjKtRIw=');
 
    request('GET', base_url + '/getMasterchainInfo', (response)=> {
      let seqno = response['result']['last']['seqno'];
      console.log('Block height is: ', seqno);
    }, {});
 
 
    function get_transfer_boc(private_key, seqno) {
      const { PrivateKey, HexCoding, CoinType, AnySigner } = globalThis.core;
 
      let privateKeyData = HexCoding.decode(private_key);
 
      let transfer = TW.TheOpenNetwork.Proto.Transfer.create({
          walletVersion: TW.TheOpenNetwork.Proto.WalletVersion.WALLET_V4_R2,
          dest: "EQDYW_1eScJVxtitoBRksvoV9cCYo4uKGWLVNIHB1JqRR3n0",
          amount: new Long(10),
          sequenceNumber: seqno,
          mode: (TW.TheOpenNetwork.Proto.SendMode.IGNORE_ACTION_PHASE_ERRORS),
          expireAt: 1681132440
      });
 
      let input = TW.TheOpenNetwork.Proto.SigningInput.create({
          transfer: transfer,
          privateKey: PrivateKey.createWithData(privateKeyData).data(),
      });
 
      const encoded = TW.TheOpenNetwork.Proto.SigningInput.encode(input).finish();
      let outputData = AnySigner.sign(encoded, CoinType.theOpenNetwork);
      let output = TW.TheOpenNetwork.Proto.SigningOutput.decode(outputData);
 
      return output.encoded;
    }
 
    request('GET', base_url + '/getWalletInformation?address=EQDTOhnuvYwNNZxpOHw--72oKKMGlcbLLl7cW_JimtfPyW1C', (response)=> {
      let seqno = response['result']['seqno'];
 
      let private_key_to_check = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";
      let private_key_to_send = "4c6f6ee7e07acb8619264eb934600a5eff2bf2c986e6ec5c8bb536ce803195c0"
 
      let estimate_boc = get_transfer_boc(private_key_to_check, seqno);
      let send_boc = get_transfer_boc(private_key_to_send, seqno);
 
      let estimate_fee_data = {
        "address": "EQDTOhnuvYwNNZxpOHw--72oKKMGlcbLLl7cW_JimtfPyW1C",
        "body": estimate_boc,
        "init_code": "",
        "init_data": "",
        "ignore_chksig": true
      }
  
      request('POST', base_url + '/estimateFee', (response) => {
        let fees = response['result']['source_fees']
        let fee = fees['in_fwd_fee'] + fees['storage_fee'] + fees['gas_fee'] + fees['fwd_fee']
        console.log('Fee for sending transaction: ', fee / 1e9);
      }, estimate_fee_data);
 
 
      let send_boc_data = {
        "boc": send_boc
      }
      request('POST', base_url + '/sendBocReturnHash', (response) => {
        console.log('Transaction sent: ', response['result']['hash']);
      }, send_boc_data);
 
    }, {});
  });
 