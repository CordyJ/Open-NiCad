//
//  TermsAndConditionsViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-09.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import WebKit

class TermsAndConditionsViewController: UIViewController {

   @IBOutlet private var closeButton : UIButton!

    var dismiss: (()->())?
    fileprivate var webView = WKWebView()
    
    override var prefersStatusBarHidden : Bool {
        return true
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()

        if let URL = Bundle.main.url(forResource: Constants.TermsAndConditionsFilename, withExtension: "html") {
            webView.loadFileURL(URL, allowingReadAccessTo: URL)
        }
        webView.isOpaque = false
        webView.backgroundColor = UIColor.clear
        webView.scrollView.backgroundColor = UIColor.clear

        self.view.addSubview(webView)
		self.view.sendSubviewToBack(webView)
        webView.snp.makeConstraints({ (make) in
            make.edges.equalTo(self.view)
        })

    }
    
    @IBAction private func dismissTapped(_ sender:UIButton) {
        dismiss?()
    }
   
   
   func setBackgroundColor( colorToUse : UIColor )
   {
        webView.backgroundColor = colorToUse
   }
   


   func hideCloseButton()
   {
      closeButton.isHidden = true
   }
   
   
   func setURLToLoad( url : String )
   {
        if let URL = Bundle.main.url(forResource: url, withExtension: "html")
        {
            webView.loadFileURL(URL, allowingReadAccessTo: URL)
        }
   }
}
