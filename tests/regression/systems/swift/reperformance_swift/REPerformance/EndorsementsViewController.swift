//
//  EndorsementsViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-23.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import youtube_ios_player_helper

struct EndorsementsViewData{
    let player1Name:String
    let player1Description:String
    let player2Name:String
    let player2Description:String
    let player3Name:String
    let player3Description:String
    
    init(player1Name:String, player1Description:String, player2Name:String, player2Description:String, player3Name:String, player3Description:String) {
        self.player1Name = player1Name
        self.player1Description = player1Description
        self.player2Name = player2Name
        self.player2Description = player2Description
        self.player3Name = player3Name
        self.player3Description = player3Description
    }
}

class EndorsementsViewController: UIViewController {
    
	@IBOutlet private var endorsementVideoView: YTPlayerView? {
		didSet {
			self.endorsementVideoView?.load(withVideoId: Constants.OurValue.EndorsementsVideoYouTubeID)
		}
	}
    
    @IBOutlet private var player1NameLabel:UILabel?
    @IBOutlet private var player1DescriptionLabel:UILabel?
    @IBOutlet private var player2NameLabel:UILabel?
    @IBOutlet private var player2DescriptionLabel:UILabel?
    @IBOutlet private var player3NameLabel:UILabel?
    @IBOutlet private var player3DescriptionLabel:UILabel?
    
    var viewData:EndorsementsViewData?
	
	
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        setUpLabels()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.OurValueEndorsements, className: String(describing: self))
    }
    
    func setUpLabels() {
        player1NameLabel?.textColor = UIColor.white
        player1DescriptionLabel?.textColor = UIColor.white
        player2NameLabel?.textColor = UIColor.white
        player2DescriptionLabel?.textColor = UIColor.white
        player3NameLabel?.textColor = UIColor.white
        player3DescriptionLabel?.textColor = UIColor.white
        
        player1NameLabel?.text = viewData?.player1Name
        player1DescriptionLabel?.text = viewData?.player1Description
        player2NameLabel?.text = viewData?.player2Name
        player2DescriptionLabel?.text = viewData?.player2Description
        player3NameLabel?.text = viewData?.player3Name
        player3DescriptionLabel?.text = viewData?.player3Description
    }
}
