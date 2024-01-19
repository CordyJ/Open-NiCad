//
//  OurValueCoordinator.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-23.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

protocol OurValueItem {
    var question:String {get}
}

struct OurValueEndorsements:OurValueItem{
    let question:String
    
    init(question:String) {
        self.question = question
    }
}

struct OurValueQuestion:OurValueItem{
    let question:String
    let answer:String
    
    init(question:String, answer:String) {
        self.question = question
        self.answer = answer
    }
}

class OurValueCoordinator{
    
    let ourValueViewController:OurValueTableViewController
    let endorsementsViewController:EndorsementsViewController
    
    let questions:Array<String> = [L10n.ourValueQuestion1, L10n.ourValueQuestion2, L10n.ourValueQuestion3, L10n.ourValueQuestion4, L10n.ourValueQuestion5]
    let answers:Array<String> = [L10n.ourValueAnswer1, L10n.ourValueAnswer2, L10n.ourValueAnswer3, L10n.ourValueAnswer4, L10n.ourValueAnswer5]
    
    init() {
        ourValueViewController = StoryboardScene.OurValue.ourValueVC.instantiate()
        endorsementsViewController = StoryboardScene.OurValue.endorsementsVC.instantiate()
        ourValueViewController.title = L10n.ourValueTitle
        setUpOurValueTableViewController()
        setUpEndorsementsViewController()
    }
    
    func rootViewController() -> UIViewController{
        return ourValueViewController
    }
    
    private func setUpOurValueTableViewController() {
        ourValueViewController.viewData = getOurValueContent()
        ourValueViewController.endorsements = { [weak ourValueViewController] in
            ourValueViewController?.navigationController?.pushViewController(self.endorsementsViewController, animated: true)
        }
    }
    
    private func setUpEndorsementsViewController(){
        let viewData:EndorsementsViewData = EndorsementsViewData(player1Name: L10n.nickFolignoName, player1Description: L10n.nickFolignoDescription, player2Name: L10n.rebeccaJohnsonName, player2Description: L10n.rebeccaJohnsonDescription, player3Name: L10n.marcusFolignoName, player3Description: L10n.marcusFolignoDescription)
        endorsementsViewController.viewData = viewData
    }
    
    private func getOurValueContent() -> Array<OurValueItem>{
        let items:Array<OurValueItem> = [OurValueEndorsements(question:L10n.endorsementsCellTitle), OurValueQuestion(question:L10n.ourValueQuestion1, answer:L10n.ourValueAnswer1), OurValueQuestion(question:L10n.ourValueQuestion2, answer:L10n.ourValueAnswer2), OurValueQuestion(question:L10n.ourValueQuestion3, answer:L10n.ourValueAnswer3), OurValueQuestion(question:L10n.ourValueQuestion4, answer:L10n.ourValueAnswer4), OurValueQuestion(question:L10n.ourValueQuestion5, answer:L10n.ourValueAnswer5)]
        return items
    }
    
}
