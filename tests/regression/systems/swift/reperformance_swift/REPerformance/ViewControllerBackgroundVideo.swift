//
//  ViewControllerBackgroundVideo.swift
//
//  Created by Alan Yeung on 2017-04-25.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AVFoundation

class ViewControllerBackgroundVideo: NSObject {

    private var avplayer: AVPlayer?
    private var backgroundVideoURL: URL?

    @IBOutlet private weak var viewController: UIViewController?
    
    @IBInspectable var backgroundVideoName: String? {
        didSet {
            if let backgroundVideoName = backgroundVideoName {
                backgroundVideoURL = Bundle.main.url(forResource: backgroundVideoName, withExtension: "mp4")
            }
        }
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self, name: NSNotification.Name.AVPlayerItemDidPlayToEndTime, object: nil)
    }
    
    override func awakeFromNib() {
        if avplayer == nil {
            guard let view = viewController?.view, let videoURL = backgroundVideoURL else {
                return
            }
            
            let avAsset = AVAsset(url: videoURL)
            let avPlayerItem = AVPlayerItem(asset: avAsset)
            let moviePlayerView = UIView()
            
            avplayer = AVPlayer(playerItem: avPlayerItem)
            let avPlayerLayer = AVPlayerLayer(player: avplayer)
            avPlayerLayer.videoGravity = AVLayerVideoGravity.resizeAspectFill
            avPlayerLayer.frame = UIScreen.main.bounds
            moviePlayerView.layer.addSublayer(avPlayerLayer)

            view.insertSubview(moviePlayerView, at: 0)
            
            // config player
			avplayer?.seek(to: CMTime.zero)
            avplayer?.volume = 0.0
            avplayer?.actionAtItemEnd = .none
            
            NotificationCenter.default.addObserver(self, selector: #selector(ViewControllerBackgroundVideo.playerItemDidReachEnd(notification:)), name: NSNotification.Name.AVPlayerItemDidPlayToEndTime, object: avplayer?.currentItem)
			NotificationCenter.default.addObserver(self, selector: #selector(ViewControllerBackgroundVideo.playerStartPlaying), name: UIApplication.didBecomeActiveNotification, object: nil)
			NotificationCenter.default.addObserver(self, selector: #selector(ViewControllerBackgroundVideo.playerPausePlaying), name: UIApplication.willResignActiveNotification, object: nil)
            
            
            avplayer?.play()
        }
    }
    
    @objc func playerItemDidReachEnd(notification:NSNotification) {
        let avPlayerItem = notification.object as! AVPlayerItem
		avPlayerItem.seek(to: CMTime.zero)
    }
    
    @objc func playerStartPlaying() {
        avplayer?.play()
    }

    @objc func playerPausePlaying() {
        avplayer?.pause()
    }
}
