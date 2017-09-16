import numpy as np
from numpy import *
import math
import os
import PSFitMLData as mld
import Hal_fullres as mlc
from matplotlib import pylab as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors
# from params import mldir, trainFile, max_nClass, res_per_win, rawTrainFiles
from ml_params import *

def makeBinResImage(mlData, res_num, angle=0, phase_normalise=False, showFrames=False, dataObj=None):
    '''Creates a table with 3 rows: I, Q, and vel_iq for makeTrainData()

    inputs 
    res_num: index of resonator in question
    iAtten: index of attenuation in question
    angle: angle of rotation about the origin (radians)
    showFrames: pops up a window of the frame plotted using matplotlib.plot
    '''     
    # if dataObj is None:
    #     if mlClass.inferenceData is None:
    #         raise ValueError('Initialize dataObj first!')
    #     dataObj = mlClass.inferenceData
    
    xWidth= mlData.xWidth 

    loops=[]
    for iAtten in range(mlData.nClass):
        xCenter = argmax(mlData.iq_vels_orig[res_num,iAtten,:])
        start = int(xCenter - xWidth/2)
        end = int(xCenter + xWidth/2)

        if start < 0:
            start_diff = abs(start)
            start = 0
            iq_vels = mlData.iq_vels_orig[res_num, iAtten, start:end]
            iq_vels = np.lib.pad(iq_vels, (start_diff,0), 'constant', constant_values=(0))
            Is = mlData.Is_orig[res_num,iAtten,start:end]
            Is = np.lib.pad(Is, (start_diff,0), 'constant', constant_values=(Is[0]))
            Qs = mlData.Qs_orig[res_num,iAtten,start:end]
            Qs = np.lib.pad(Qs, (start_diff,0), 'constant', constant_values=(Qs[0]))
        elif end >= np.shape(mlData.freqs)[1]:
            iq_vels = mlData.iq_vels_orig[res_num, iAtten, start:end]
            iq_vels = np.lib.pad(iq_vels, (0,end-np.shape(mlData.freqs)[1]+1), 'constant', constant_values=(0))
            Is = mlData.Is_orig[res_num,iAtten,start:end]
            Is = np.lib.pad(Is, (0,end-np.shape(mlData.freqs)[1]), 'constant', constant_values=(Is[-1]))
            Qs = mlData.Qs_orig[res_num,iAtten,start:end]
            Qs = np.lib.pad(Qs, (0,end-np.shape(mlData.freqs)[1]), 'constant', constant_values=(Qs[-1]))
        else:
            iq_vels = mlData.iq_vels_orig[res_num, iAtten, start:end]
            Is = mlData.Is_orig[res_num,iAtten,start:end]
            Qs = mlData.Qs_orig[res_num,iAtten,start:end]
        #iq_vels = np.round(iq_vels * xWidth / max(mlData.iq_vels[res_num, iAtten, :]) )
        
        iq_vels = iq_vels / np.amax(mlData.iq_vels[res_num, :, :])
        res_mag = math.sqrt(np.amax(mlData.Is[res_num, :, :]**2 + mlData.Qs[res_num, :, :]**2))
        Is = Is / res_mag
        Qs = Qs / res_mag

        # Is = Is /np.amax(mlData.iq_vels[res_num, :, :])
        # Qs = Qs /np.amax(mlData.iq_vels[res_num, :, :])

        # Is = Is /np.amax(mlData.Is[res_num, :, :])
        # Qs = Qs /np.amax(mlData.Qs[res_num, :, :])



        if angle != 0:
            rotMatrix = np.array([[np.cos(angle), -np.sin(angle)], 
                                     [np.sin(angle),  np.cos(angle)]])

            Is,Qs = np.dot(rotMatrix,[Is,Qs])



        image = np.zeros((len(Is),3))
        image[:,0] = Is
        image[:,1] = Qs
        image[:,2] = iq_vels

        loops.append(image)

    if max_nClass != mlData.nClass:
        padding = np.zeros((max_nClass-len(loops),mlData.xWidth,3))
        loops = np.concatenate([loops,padding],axis=0)


    loops = loops * np.ones((len(loops),mlData.xWidth,3))
    if showFrames:
        plot_res(loops)

    return loops

def makeResImage(mlData, res_num, angle=0, pert=0, scale = 1, window=None, phase_normalise=False, showFrames=False, dataObj=None):
    '''Creates a table with 3 rows: I, Q, and vel_iq for makeTrainData()

    inputs 
    res_num: index of resonator in question
    iAtten: index of attenuation in question
    angle: angle of rotation about the origin (radians)
    showFrames: pops up a window of the frame plotted using matplotlib.plot
    '''     
    # if dataObj is None:
    #     if mlClass.inferenceData is None:
    #         raise ValueError('Initialize dataObj first!')
    #     dataObj = mlClass.inferenceData
    
    xWidth= mlData.xWidth 

    loops=[]
    # for iAtten in range(mlData.nClass):
    for iAtten in range(max_nClass):
        xCenter = get_peak_idx(mlData,res_num,iAtten)
        if pert != 0:
            xCenter = xCenter + pert
        start = int(xCenter - xWidth/2)
        end = int(xCenter + xWidth/2)

        if start < 0:
            start_diff = abs(start)
            start = 0
            iq_vels = mlData.iq_vels[res_num, iAtten, start:end]
            iq_vels = np.lib.pad(iq_vels, (start_diff,0), 'constant', constant_values=(0))
            Is = mlData.Is[res_num,iAtten,start:end]
            Is = np.lib.pad(Is, (start_diff,0), 'constant', constant_values=(Is[0]))
            Qs = mlData.Qs[res_num,iAtten,start:end]
            Qs = np.lib.pad(Qs, (start_diff,0), 'constant', constant_values=(Qs[0]))
        elif end >= np.shape(mlData.freqs)[1]:
            iq_vels = mlData.iq_vels[res_num, iAtten, start:end]
            iq_vels = np.lib.pad(iq_vels, (0,end-np.shape(mlData.freqs)[1]+1), 'constant', constant_values=(0))
            Is = mlData.Is[res_num,iAtten,start:end]
            Is = np.lib.pad(Is, (0,end-np.shape(mlData.freqs)[1]), 'constant', constant_values=(Is[-1]))
            Qs = mlData.Qs[res_num,iAtten,start:end]
            Qs = np.lib.pad(Qs, (0,end-np.shape(mlData.freqs)[1]), 'constant', constant_values=(Qs[-1]))
        else:
            iq_vels = mlData.iq_vels[res_num, iAtten, start:end]
            Is = mlData.Is[res_num,iAtten,start:end]
            Qs = mlData.Qs[res_num,iAtten,start:end]
        #iq_vels = np.round(iq_vels * xWidth / max(mlData.iq_vels[res_num, iAtten, :]) )
        
        iq_vels = iq_vels / np.amax(mlData.iq_vels[res_num, :, :])
        res_mag = math.sqrt(np.amax(mlData.Is[res_num, :, :]**2 + mlData.Qs[res_num, :, :]**2))
        # print mlData.Is[res_num, :, :], res_mag
        Is = Is / res_mag
        Qs = Qs / res_mag

        if scale != 1:
            Is = Is * scale
            Qs = Qs * scale
            iq_vels = iq_vels * scale
        # Is = Is /np.amax(mlData.iq_vels[res_num, :, :])
        # Qs = Qs /np.amax(mlData.iq_vels[res_num, :, :])

        # Is = Is /np.amax(mlData.Is[res_num, :, :])
        # Qs = Qs /np.amax(mlData.Qs[res_num, :, :])

        # angle =math.pi/2 
        if angle != 0:
            #mags = Qs**2 + Is**2
            #mags = map(lambda x: math.sqrt(x), mags)#map(lambda x,y:x+y, a,b)

            #peak_idx = self.get_peak_idx(res_num,iAtten)
            # peak_idx =argmax(iq_vels)
            # #min_idx = argmin(mags)

            # phase_orig = math.atan2(Qs[peak_idx],Is[peak_idx])
            # #phase_orig = math.atan2(Qs[min_idx],Is[min_idx])

            # angle = -phase_orig

            rotMatrix = np.array([[np.cos(angle), -np.sin(angle)], 
                                     [np.sin(angle),  np.cos(angle)]])

            Is,Qs = np.dot(rotMatrix,[Is,Qs])

        if window != None:
            Is[:window[0]] = Is[window[0]+1]
            Is[-window[1]:] = Is[-window[1]-1]
            Qs[:window[0]] = Qs[window[0]+1]
            Qs[-window[1]:] = Qs[-window[1]-1]
            iq_vels[:window[0]] = 0
            iq_vels[-window[1]:] = 0

        image = np.zeros((len(Is),3))
        image[:,0] = Is
        image[:,1] = Qs
        image[:,2] = iq_vels

        loops.append(image)

    # if max_nClass != mlData.nClass:
    #     padding = np.zeros((max_nClass-len(loops),mlData.xWidth,3))
    #     loops = np.concatenate([loops,padding],axis=0)
    # SMALL_SIZE = 14
    # MEDIUM_SIZE = 18
    # BIGGER_SIZE = 22

    # plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    # plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    # plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    # plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    # plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    # plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    # #plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    # plt.figure(figsize=(8,8))
    # # plt.plot(loops[3][:,0],loops[3][:,1], '-o')
    # plt.plot(loops[3][:,0])
    # # plt.xlabel('I')
    # plt.ylabel('I')
    # plt.figure(figsize=(8,8))
    # # plt.plot(loops[3][:,0],loops[3][:,1], '-o')
    # plt.plot(loops[3][:,1])
    # # plt.xlabel('I')
    # plt.ylabel('Q')
    # plt.show()
    loops = loops * np.ones((len(loops),mlData.xWidth,3))
    if showFrames:
        plot_res(loops)

    return loops

def plot_res(loops):
    iAtten_view =  np.arange(0,np.shape(loops)[0],5)

    f, axarr = plt.subplots(len(iAtten_view),3,figsize=(5.0, 8.1))
    # axarr[0,1].set_title(iAtten)
    for i,av in enumerate(iAtten_view):
        axarr[i,0].plot(loops[av,:,2])
        axarr[i,0].set_ylabel(av)
        axarr[i,1].plot(loops[av,:,0])
        axarr[i,1].plot(loops[av,:,1])
        axarr[i,2].plot(loops[av,:,0],loops[av,:,1])
    plt.show()
    plt.close()

def plot_max_ratio(datacube):
    print np.shape(datacube)
    datacube = np.asarray(datacube)
    iqv = datacube[:,:,2]
    print np.shape(iqv)
    max_iqv = np.max(iqv, axis =1)
    vindx = np.argmax(iqv, axis =1)
    print np.shape(max_iqv)
    print vindx

    max_ratio = np.zeros((max_nClass))
    for ia in range(max_nClass):
        if vindx[ia] == 0:
            max_neighbor = iqv[ia,1]
        elif vindx[ia] == len(iqv[ia,:])-1:
            max_neighbor = iqv[ia,vindx[ia]-1]
        else:
            max_neighbor = np.maximum(iqv[ia,vindx[ia]-1],iqv[ia,vindx[ia]+1])

        max_ratio[ia] = (iqv[ia,vindx[ia]]/ max_neighbor)

    SMALL_SIZE = 14
    MEDIUM_SIZE = 18
    BIGGER_SIZE = 22

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    #plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    plt.figure(figsize=(6,6))
    # plt.plot(loops[3][:,0],loops[3][:,1], '-o')
    # plt.xlabel('I')
    plt.ylabel('max($v_{IQ}$)/2$^{nd}$max($v_{IQ}$)')
    plt.xlabel('Attenuation (dB)')

    guess = 1 
    plt.plot(range(46,46+max_nClass), max_ratio,'-o', label='ratio')
    plt.axhline(1.75, color='k', linestyle='--', label='threshold')
    plt.plot(46+guess, max_ratio[guess], color='g', marker='o')
    plt.grid(True)
    
    I = datacube[:,:,0]
    Q = datacube[:,:,1]


    plt.figure(figsize=(6,6))
    for i in range(0,3):
        plt.plot(I[i], Q[i], '-ob')
        if i == guess:
            plt.plot(I[i], Q[i], '-og')
    # plt.plot(I[guess], Q[guess], '-og')
    # plt.plot(I[guess-1], Q[guess-1], '-ob', alpha=0.8)
    # plt.plot(I[guess-2], Q[guess-2], '-ob', alpha=0.6)
    plt.grid(True)
    plt.xlabel('I (A.U)')
    plt.ylabel('Q (A.U)')
    plt.show()


def get_peak_idx(mlData,res_num,iAtten):
    # if dataObj is None:
    #     if mlData.inferenceData is None:
    #         raise ValueError('Initialize dataObj first!')
    #     dataObj = mlData.inferenceData
    return argmax(mlData.iq_vels[res_num,iAtten,:])

def plotWeights(weights):
    '''creates a 2d map showing the positive and negative weights for each class'''
    # weights = [mlClass.sess.run(mlClass.W_conv1), mlClass.sess.run(mlClass.W_conv2)]
    print np.shape(weights)
    f, axarr = plt.subplots(3,3,figsize=(20.0, 4))
    axarr[2,1].set_xlabel('freq?')
    axarr[1,0].set_ylabel('atten?')
    for filt in range(3):
        for i, w in enumerate(weights):
            for out in range(np.shape(w)[2]):
                for a in range(np.shape(w)[0]):
                    axarr[i,filt].plot(w[a,:,out,filt])

    plt.show()

    f, axarr = plt.subplots(3,3,figsize=(20.0, 4))
    axarr[2,1].set_xlabel('freq?')
    axarr[1,0].set_ylabel('atten?')
    for filt in range(3):
        for i, w in enumerate(weights):
            # print np.shape(w)
            # plt.subplot(4,3,(i+1)*(row+1))
            im = axarr[i,filt].imshow(w[:,:,0,filt], cmap=cm.coolwarm, interpolation='none',aspect='auto')
            # plt.plot(weights[0,:,0, nc])
            plt.title(' %i' % i)


    f.subplots_adjust(right=0.8)
    cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
    f.colorbar(im, cax=cbar_ax)

    plt.show()
    plt.close()

def plot_input_cube(loops):
    # print np.shape(activations)
    SMALL_SIZE = 18
    MEDIUM_SIZE = 22
    BIGGER_SIZE = 26

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    #plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    # plt.figure(figsize=(8,8))



    # # create a 21 x 21 vertex mesh
    # xx, yy = np.meshgrid(np.linspace(0,50,50), np.linspace(0,3,3))
    xx, yy = np.meshgrid(np.arange(50), np.arange(3))

    # # # create vertices for a rotated mesh (3D rotation matrix)
    X =  xx 
    Y =  yy
    # Z =  10*np.ones(X.shape)

    # # create some dummy data (20 x 20) for the image
    # data = np.cos(xx) * np.cos(xx) + np.sin(yy) * np.sin(yy)

    # create the figure
    fig = plt.figure(figsize=(8,8))

    # show the reference image

    # for ia in range(15):
    #     # ax1 = fig.add_subplot(111)
    #     plt.imshow(np.rot90(loops[0][ia]), cmap=cm.coolwarm, origin ='lower', interpolation='none', aspect='auto')
    #     plt.show()

    # show the 3D rotated projection
    ax2 = fig.add_subplot(111, projection='3d')
    print np.shape(loops)
    for ia in range(max_nClass):
        print ia
        cset = ax2.contourf(X, Y, np.rot90(loops[0][ia]), 100, zdir='z',interpolation='none', offset=ia, cmap=cm.coolwarm)
        # plt.imshow(np.rot90(loops[0][ia]), cmap=cm.coolwarm, origin ='lower', zdir='z',interpolation='none', offset=ia * 0.2,  aspect='auto')
        # cset = ax2.plot_surface(X, Y,  np.rot90(loops[0][ia]), rstride=1, cstride=1, facecolors=plt.cm.BrBG(np.rot90(loops[0][ia])), shade=False)
    
    ax2.set_zlim((0.,max_nClass))
    ax2.set_yticks([0,1,2])
    ax2.set_xlabel('freq samples')
    ax2.set_ylabel('$v_{IQ}$    Q   I')
    ax2.set_zlabel('atten samples')
    plt.colorbar(cset)
    plt.show()

def plotActivations(activations):
    '''creates a 2d map showing the positive and negative weights for each class'''
    _,_,testImages,_ = mld.loadPkl(mldir+trainFile)

    # activations = [mlClass.sess.run(mlClass.x_image,feed_dict={mlClass.x: testImages}), 
    #             mlClass.sess.run(mlClass.h_conv1, feed_dict={mlClass.x: testImages}),
    #             mlClass.sess.run(mlClass.h_pool1, feed_dict={mlClass.x: testImages}),
    #             mlClass.sess.run(mlClass.h_conv2, feed_dict={mlClass.x: testImages}),
    #             mlClass.sess.run(mlClass.h_pool2, feed_dict={mlClass.x: testImages})]

    # f, ax = plt.subplots(111)
    plt.close()

    # self.sess.run(x_image,feed_dict={self.x: testImages}),
    print np.shape(activations[1][0,3,:,:]), np.shape(activations[1])
    for ia in range(len(activations)):
        plt.imshow(np.rot90(activations[ia][0,3,:,:]), cmap=cm.coolwarm,interpolation='none', aspect='auto')
        plt.show()
        plt.close()


    print np.shape(activations[0])
    for r in range(len(testImages)):
        # for p in range(max_nClass):
        #     print p
        f, axarr = plt.subplots(len(activations)+1,8,figsize=(16.0, 8.1))
        p=6

        axarr[0,0].plot(activations[0][r,p,:,0],activations[0][r,p,:,1])
        for ir, row in enumerate(range(1, 4)):
            axarr[0,ir].axis('off')
            axarr[0,row].plot(activations[0][r,p,:,ir])
        # print np.arange(0,max_nClass,2)
        for ir, row in enumerate(np.arange(0,max_nClass,2)):
            for i, a in enumerate(activations):
                axarr[i+1,ir].axis('off')
                im = axarr[i+1,ir].imshow(np.rot90(a[r,row,:,:]), cmap=cm.coolwarm,interpolation='none', aspect='auto')#aspect='auto'
            # if row==2:
            #     axarr[i+2,row].colorbar(cmap=cm.afmhot)
        f.subplots_adjust(right=0.8)
        cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
        f.colorbar(im, cax=cbar_ax)
        
        plt.show()
        plt.close()

def checkLoopAtten(inferenceData, res_num, iAtten, showFrames=False):
    '''A function to analytically check the properties of an IQ loop: saturatation and smoothness.

    To check for saturation if the ratio between the 1st and 2nd largest edge is > max_ratio_threshold.
    
    Another metric which is more of a proxy is if the angle on either side of the sides connected to the 
    longest edge is < min_theta or > max_theta the loop is considered saturated. 

    A True result means that the loop is unsaturated.

    Inputs:
    res_num: index of resonator in question
    iAtten: index of attenuation in question
    showLoop: pops up a window of the frame plotted 

    Output:
    Theta 1 & 2: used as a proxy for saturation
    Max ratio: the ratio of highest and 2nd highest v_iq - a more reliable indicator of saturation
    vels: angles every 3 points make around the loop. The closer each to ~ 160 deg the smoother the loop
    '''
    # vindx = (-inferenceData.iq_vels[res_num,iAtten,:]).argsort()[:1]
    # print vindx    
    vindx = np.argmax(inferenceData.iq_vels[res_num,iAtten,:])

    if vindx == 0:
        max_neighbor = inferenceData.iq_vels[res_num, iAtten,1]
    elif vindx == len(inferenceData.iq_vels[res_num,iAtten,:])-1:
        max_neighbor = inferenceData.iq_vels[res_num,iAtten,vindx-1]
    else:
        max_neighbor = maximum(inferenceData.iq_vels[res_num,iAtten,vindx-1],inferenceData.iq_vels[res_num, iAtten,vindx+1])

    max_theta_vel  = math.atan2(inferenceData.Qs[res_num,iAtten,vindx-1] - inferenceData.Qs[res_num,iAtten,vindx], 
                                inferenceData.Is[res_num,iAtten,vindx-1] - inferenceData.Is[res_num,iAtten,vindx])
    low_theta_vel = math.atan2(inferenceData.Qs[res_num,iAtten,vindx-2] - inferenceData.Qs[res_num,iAtten,vindx-1], 
                               inferenceData.Is[res_num,iAtten,vindx-2] - inferenceData.Is[res_num,iAtten,vindx-1])
    upp_theta_vel = math.atan2(inferenceData.Qs[res_num,iAtten,vindx] - inferenceData.Qs[res_num,iAtten,vindx+1], 
                               inferenceData.Is[res_num,iAtten,vindx] - inferenceData.Is[res_num,iAtten,vindx+1])


    # print (inferenceData.iq_vels[res_num,iAtten,vindx]/ max_neighbor)
    max_ratio = (inferenceData.iq_vels[res_num,iAtten,vindx]/ max_neighbor)

    theta1 = (math.pi + max_theta_vel - low_theta_vel)/math.pi * 180
    theta2 = (math.pi + upp_theta_vel - max_theta_vel)/math.pi * 180

    theta1 = abs(theta1)
    if theta1 > 360:
        theta1 = theta1-360
    theta2= abs(theta2)
    if theta2 > 360:
        theta2 = theta2-360

    if showFrames:
        plt.plot(inferenceData.Is[res_num,iAtten,:],inferenceData.Qs[res_num,iAtten,:], 'g.-')
        plt.show()
    
    vels = np.zeros((len(inferenceData.Is[res_num,iAtten,:])-2))
    # for i,_ in enumerate(vels[1:-1]):
    for i,_ in enumerate(vels, start=1):
        low_theta_vel = math.atan2(inferenceData.Qs[res_num,iAtten,i-1] - inferenceData.Qs[res_num,iAtten,i], 
                                   inferenceData.Is[res_num,iAtten,i-1] - inferenceData.Is[res_num,iAtten,i])
        if low_theta_vel < 0: 
            low_theta_vel = 2*math.pi+low_theta_vel
        upp_theta_vel = math.atan2(inferenceData.Qs[res_num,iAtten,i+1] - inferenceData.Qs[res_num,iAtten,i], 
                                   inferenceData.Is[res_num,iAtten,i+1] - inferenceData.Is[res_num,iAtten,i])
        if upp_theta_vel < 0: 
            upp_theta_vel = 2*math.pi+upp_theta_vel
        vels[i-1] = abs(upp_theta_vel- low_theta_vel)/math.pi * 180

    return [theta1, theta2, max_ratio, vels]


def checkResAtten(inferenceData, res_num, plotAngles=False, showResData=False, min_theta = 115, max_theta = 220, max_ratio_threshold = 2.5):
    '''
    Outputs useful properties about each resonator using checkLoopAtten.
    Figures out if a resonator is bad using the distribution of angles around the loop
    Analytically finds the attenuation values when the resonator is saturated using the max ratio metric and adjacent angles to max v_iq line metric 

    Inputs:
    min/max_theta: limits outside of which the loop is considered saturated
    max_ratio_threshold: maximum largest/ 2nd largest IQ velocity allowed before loop is considered saturated
    showFrames: plots all the useful information on one plot for the resonator

    Oututs:
    Angles non sat: array of bools (true is non sat)
    Ratio non sat: array of bools (true is non sat)
    Ratio: ratio in v_iq between 1st and next highest adjacent max
    Running ratio: Ratio but smoothed using a running average
    Bad res: using the distribution of angles bad resonators are identified (true is bad res)
    Angles mean center: the mean of the angles around the center of the distribution (should be ~ 160)
    Angles std center: the standard dev of the angles. In the center they should follow a gauss dist and the tighter the better 
    '''
    nattens = np.shape(inferenceData.attens)[1]
    max_ratio_threshold = np.linspace(0,max_ratio_threshold*7,int(nattens))
    # max_ratio = inferenceData.iq_vels[res_num,iAtten,vindx[0]]/ inferenceData.iq_vels[res_num,iAtten,vindx[1]]

    max_theta = np.linspace(max_theta,max_theta*1.2,int(nattens))
    min_theta = np.linspace(min_theta,min_theta/1.2,int(nattens))

    angles = np.zeros((nattens,2))
    ratio = np.zeros(nattens)

    angles_nonsat = np.ones(nattens)
    ratio_nonsat = np.zeros(nattens)


    running_ratio = np.zeros((nattens))  

    vels = np.zeros((np.shape(inferenceData.iq_vels[0])[0], np.shape(inferenceData.iq_vels[0])[1]-1))


    # for ia, _ in enumerate(inferenceData.attens):
    for ia in range(nattens):
        loop_sat_cube = checkLoopAtten(inferenceData,res_num,iAtten=ia, showFrames=False)
        angles[ia,0], angles[ia,1], ratio[ia], vels[ia] = loop_sat_cube
        ratio_nonsat[ia] = ratio[ia] < max_ratio_threshold[ia]
        
    angles_running =  np.ones((nattens,2))*angles[0,:]
    for ia in range(1,nattens):
        angles_running[ia,0] = (angles[ia,0] + angles_running[ia-1,0])/2
        angles_running[ia,1] = (angles[ia,1] + angles_running[ia-1,1])/2
        # running_ratio[-ia] = np.sum(ratio[-ia-1: -1])/ia
        running_ratio[-ia-1] = (running_ratio[-ia] + ratio[-ia-1])/2

    # for ia in range(1,nattens-2):
    #     diff_rr[ia] = sum(running_ratio[ia-1:ia])-sum(running_ratio[ia+1:ia])

    for ia in range(nattens/2):
        angles_nonsat[ia] = (max_theta[ia] > angles_running[ia,0] > min_theta[ia]) and (max_theta[ia] > angles_running[ia,1] > min_theta[ia])

    angles_mean_center = np.mean(vels[:,35:115], axis =1)
    angles_std_center = np.std(vels[:,35:115], axis=1)
    angles_mean = np.mean(vels,axis=1)
    angles_std = np.std(vels,axis=1)

    delim = np.shape(vels)[1]/3

    y, x = np.histogram(vels[:,50:100])
    x = x[:-1]
    
    angles_dist = np.zeros((nattens,len(y)))
    # angles_mean_correct=np.zeros(nattens))
    # angles_std_correct=np.zeros((nattens))

    for ia in range(nattens):
        angles_dist[ia],_ = np.histogram(vels[ia,:])
        tail = np.linspace(angles_dist[ia,0],angles_dist[ia,-1],len(angles_dist[ia]))
        angles_dist[ia] = abs(angles_dist[ia] - tail)
        # angles_mean_correct[ia] = mean(x,angles_dist[ia])
        # angles_std_correct[ia] = std(x,angles_dist[ia],angles_mean_correct[ia])

    tail = np.linspace(y[0],y[-1],len(y))
    y = y - tail
    mid_x = x[4:8]
    mid_y = y[4:8]
    
    # def mean(x, y):
    #     return sum(x*y) /sum(y)
    # def std(x,y,mean):
    #     return np.sqrt(sum(y * (x - mean)**2) / sum(y))
    # def Gauss(x, a, x0, sigma):
    #     return a * np.exp(-(x - x0)**2 / (2 * sigma**2))
    # from scipy.optimize import curve_fit
    # # correction for weighted arithmetic mean
    # mean = mean(x,y)
    # # mean = 153
    # sigma = std(x,y,mean)
    # varience = 5
    # print mean, sigma
    # popt,pcov = curve_fit(Gauss, mid_x, mid_y, p0=[max(y), mean, sigma])
    # chi2 = sum((mid_y- Gauss(mid_x, *popt))**2 / varience**2 )
    # dof = len(mid_y)-3

    if plotAngles:
        plt.title(res_num)
        plt.plot(x, y, 'b:', label='data')
        # plt.plot(mid_x, Gauss(mid_x, *popt), 'r--', label='fit')
        # plt.plot(mid_x,mid_y -  Gauss(mid_x, *popt), label='residual')
        # plt.legend()
        plt.xlabel('Angle')
        plt.show()
        # for ia,_ in enumerate(nattens):
        #     plt.plot(x, angles_dist[ia], 'b:', label='data')
        #     plt.show()

    # if chi2 < 100
    if np.all(angles_std_center > 80):
        print 'yes', angles_std_center
    if max(mid_y)<0:
            bad_res = True
    else: bad_res = False

    if showResData:
        fig, ax1 = plt.subplots()

        # ax1.plot(inferenceData.attens,angles[:,0],'b')
        # ax1.plot(inferenceData.attens,angles[:,1],'g')
        ax1.plot(inferenceData.attens,angles_running,'g')
        ax1.plot(inferenceData.attens,vels, 'bo',alpha=0.2)
        # ax1.plot(inferenceData.attens,angles_dist, 'bo',alpha=0.2)
        ax1.plot(inferenceData.attens,min_theta, 'k--')
        ax1.plot(inferenceData.attens,max_theta, 'k--')
        ax1.plot(inferenceData.attens,angles_mean)
        ax1.plot(inferenceData.attens,angles_std, 'r')
        ax1.plot(inferenceData.attens,angles_mean_center, 'b--')
        ax1.plot(inferenceData.attens,angles_std_center, 'r--')
        ax1.set_xlabel('Atten index')
        ax1.set_ylabel('Angles')
        ax1.set_title(res_num)
        for tl in ax1.get_yticklabels():
            tl.set_color('b')

        # ax2 = ax1.twinx()
        # ax2.plot(inferenceData.attens,ratio, 'r', label='ratio')
        # ax2.plot(inferenceData.attens,max_ratio_threshold, 'k--', label='thresh')
        # ax2.set_ylabel('Ratios')
        # for tl in ax2.get_yticklabels():
        #     tl.set_color('r')
        # plt.legend()

        # ax3 = ax1.twinx()
        # ax3.plot(inferenceData.attens,angles_nonsat, 'purple', label='angles_nonsat')
        # ax3.plot(inferenceData.attens,ratio_nonsat, 'crimson', label='ratio_nonsat')
        # fig.subplots_adjust(right=0.75)
        # ax3.spines['right'].set_position(('axes', 1.2))
       

        ax4 = ax1.twinx()
        
        from matplotlib import cm
        import matplotlib.colors
        # ax4.autoscale(False)
        ax4.imshow(angles_dist.T,interpolation='none',cmap=cm.coolwarm,alpha=0.5, origin='lower',extent=[inferenceData.attens[0],inferenceData.attens[-1],0,len(x)], aspect='auto')
        # ax4.legend()
        # plt.colorbar(cmap=cm.afmhot)
        # ax4.set_ylim(0,10)
        plt.show() 

    return [angles_nonsat,ratio_nonsat, ratio, running_ratio, bad_res, angles_mean_center, angles_std_center]

# def normalise_train():

def plot_agree_prof(guesses_map):
    def kth_diag_indices(a, k):
        rows, cols = np.diag_indices_from(a)
        if k < 0:
            return rows[-k:], cols[:k]
        elif k > 0:
            return rows[:-k], cols[k:]
        else:
            return rows, cols

    diags = []
    red_vars = np.zeros((-1 + max_nClass*2))
    diag_correction = np.concatenate([np.arange(max_nClass-1, 0, -1), np.arange(0, max_nClass, 1)])
    # print diag_correction
    diag_form = np.zeros((max_nClass*2)-1)
    for ik, k in enumerate(range(-max_nClass+1, max_nClass)):
        # print k
        z = kth_diag_indices(np.rot90(guesses_map),k)
        diags.append( np.rot90(guesses_map)[z] )
        
        mean = (float(len(diags[ik]))-1)/2
        # print mean
        # print diags[ik]
        var = diags[ik]*(np.arange(len(diags[ik])) - mean)**2
        # print var, sum(var)
        red_vars[ik] = sum(var)/len(var)
        # plt.plot(diags[ik])
        # plt.show()
        # print diag_correction[ik], len(diags[ik]),
        diag_ind = np.arange(diag_correction[ik], diag_correction[ik] + 2*len(diags[ik]), 2)
        # print diag_ind
        # diag_form[diag_correction[ik]:diag_correction[ik]+len(diags[ik])] += diags[ik]
        diag_form[diag_ind] += diags[ik]
        # print diag_form
        # plt.plot(diag_form)

        # plt.show()

    # diag_form = diag_form/(-1 + max_nClass*2)
    diag_form = diag_form[::-1]

    # plt.figure()
    # plt.plot(red_vars)
    av_red_vars = sum(red_vars)/len(red_vars)
    print 'av red vars: ', av_red_vars

    plt.figure(figsize=(7,7))

    match_disp = np.arange(-float(max_nClass)/2 +0.75, float(max_nClass)/2 + 0.25, 0.5)

    plt.step(match_disp, diag_form, 'k')
    plt.axvline(0, linestyle='--')
    plt.xlabel('Match Displacement') # Agreemement profile
    # plt.text(5, max(diag_form), '$\sigma^{2}=$%.3f' % av_red_vars)
    plt.figtext(0.73, 0.83, '$\sigma^{2}=$%.3f' % av_red_vars)
    # plt.show()
    

def plot_confusion(independent, dependent, xlabel='True Class', ylabel='Evaluated Class'):
    # def plotComparison(rawTrainData, atten_guess):
    # rawTrainData.opt_iAttens = rawTrainData.opt_iAttens[:len(atten_guess)]

    SMALL_SIZE = 14
    MEDIUM_SIZE = 18
    BIGGER_SIZE = 22

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    #plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    plt.figure(figsize=(10,10))
    # plt.plot(loops[3][:,0],loops[3][:,1], '-o')
    # plt.xlabel('I')

    # print np.shape(dependent), np.shape(independent), dependent[:10], independent[:10]

    guesses_map = np.zeros((max_nClass,max_nClass))
    for ia,ao in enumerate(independent):   
        ag = dependent[ia]
        guesses_map[ag,ao] += 1

    from matplotlib import cm
    import matplotlib.colors
    plt.imshow(guesses_map, interpolation='none', origin='lower', cmap=cm.coolwarm) #,norm = matplotlib.colors.LogNorm())
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim([-0.5,19.5])
    plt.ylim([-0.5,19.5])
    plt.colorbar(cmap=cm.afmhot)

    plt.plot(range(max_nClass), linestyle='--')

    plot_agree_prof(guesses_map)

    # plt.figure(figsize=(6,6))
    # # plt.plot(np.sum(guesses_map, axis=0), label='True')
    # # plt.plot(np.sum(guesses_map, axis=1), label='Evaluated')
    # plt.hist(independent, range(max_nClass+1), label='True', facecolor='blue', alpha=0.65) 
    # plt.hist(dependent, range(max_nClass+1), label='Evaluated', facecolor='green', alpha=0.65)
    # print np.histogram(dependent, range(max_nClass + 1))
    # plt.legend(loc="upper left")
    plt.show()

def plot_accuracy(train_ce, test_ce, train_acc, test_acc):
    # if accuracy_plot == 'post':
    fig = plt.figure(frameon=False,figsize=(15.0, 5.0))
    fig.add_subplot(121)
    print trainReps, len(np.arange(0,trainReps,10)), len(train_ce), len(np.arange(0,trainReps,100)), len(test_ce,)
    plt.plot(np.arange(0,trainReps,10), train_ce, label='train')
    plt.plot(np.arange(0,trainReps,100), test_ce, label='test')
    plt.legend(loc='upper right')
    fig.add_subplot(122)
    plt.plot(np.arange(0,trainReps,10), train_acc, label='train')
    plt.plot(np.arange(0,trainReps,100), test_acc, label='test')
    plt.legend(loc='lower right')
    plt.show()

def plot_missed(ys_true, ys_guess, testImages, get_true_ind=True):
    # plt.plot(np.histogram(np.argmax(testLabels,1), range(21))[0])
    # plt.plot(np.histogram(ys_guess, range(21))[0])
    # plt.show()
    if get_true_ind:
        h5File = rawTrainFiles[0]
        h5File = os.path.join(mdd,h5File)
        mlData = mld.PSFitMLData(h5File = h5File)
        mlData.loadRawTrainData()

        res_nums = len(mlData.resIDs)

        # recalculate test_ind for reference 
        train_ind = np.array(map(int,np.linspace(0,res_nums-1,res_nums*mlData.trainFrac)))
        test_ind=[]
        np.asarray([test_ind.append(el) for el in range(res_nums) if el not in train_ind])

    missed = []
    for i,y in enumerate(ys_true):
        if ys_guess[i] != y:
            missed.append(i)

    for f in range(int(np.ceil(len(missed)/res_per_win))+1):
        reduced_missed = np.asarray(missed[f*res_per_win:(f+1)*res_per_win])
        print reduced_missed
        if get_true_ind:
            try:
                test_ind = np.asarray(test_ind)
                good_missed = test_ind[reduced_missed]
                print mlData.good_res[good_missed]
            except IndexError:
                pass

        _, axarr = plt.subplots(2*res_per_win, max_nClass, figsize=(16.0, 8.1))
        for r in range(res_per_win):
            for ia in range(max_nClass):
                axarr[2*r,ia].axis('off')
                axarr[(2*r)+1,ia].axis('off')
                
                try: 
                    if ia == ys_true[missed[r+f*res_per_win]]: 
                        axarr[2*r,ia].plot(testImages[missed[r+f*res_per_win]][ia,:,2], 'g')
                    elif ia == ys_guess[missed[r+f*res_per_win]]: 
                        axarr[2*r,ia].plot(testImages[missed[r+f*res_per_win]][ia,:,2], 'r')
                    else: 
                        axarr[2*r,ia].plot(testImages[missed[r+f*res_per_win]][ia,:,2], 'b')
                    if ia == ys_true[missed[r+f*res_per_win]]: 
                        axarr[(2*r)+1,ia].plot(testImages[missed[r+f*res_per_win]][ia,:,0],testImages[missed[r+f*res_per_win]][ia,:,1], 'g-o')
                    elif ia == ys_guess[missed[r+f*res_per_win]]:
                        axarr[(2*r)+1,ia].plot(testImages[missed[r+f*res_per_win]][ia,:,0],testImages[missed[r+f*res_per_win]][ia,:,1], 'r-o')
                    else: 
                        axarr[(2*r)+1,ia].plot(testImages[missed[r+f*res_per_win]][ia,:,0],testImages[missed[r+f*res_per_win]][ia,:,1], 'b-o')
                except:
                    pass

        plt.show()
        plt.close()

def view_train(trainImages, trainLabels, nClass):
    res_per_win = 4
    for f in range(int(np.ceil(len(trainLabels)/res_per_win))+1):
    
        _, axarr = plt.subplots(2*res_per_win,nClass, figsize=(16.0, 8.1))
        for r in range(res_per_win):
            print np.argmax(trainLabels[f+r],0)
            for ia in range(nClass):
                try:
                    # print f, r, missed[f+r]
                    axarr[2*r,0].set_ylabel(trainLabels[f+r])
                    # axarr[2*r,ia].axis('off')
                    # axarr[(2*r)+1,ia].axis('off')
                    if ia != np.argmax(trainLabels[r+f*res_per_win],0): axarr[2*r,ia].axis('off')
                    if ia != np.argmax(trainLabels[r+f*res_per_win],0): axarr[(2*r)+1,ia].axis('off')
                    # print np.shape(testImages[f+r,ia,:,2])
                    axarr[2*r,ia].plot(trainImages[r+f*res_per_win][ia,:,2])
                    axarr[(2*r)+1,ia].plot(trainImages[r+f*res_per_win][ia,:,0],trainImages[r+f*res_per_win][ia,:,1], '-o')
                except:
                    pass

        plt.show()
        plt.close()

def PCA(trainImages, trainLabels, max_iq):
    max_iq = np.amax(trainImages[:,:,:,2], axis=2)
    LOG_DIR = '/tmp/emb_logs/'
    metadata = os.path.join(LOG_DIR, 'metadata.tsv')
    images = tf.Variable(max_iq, name='images')
    with open(metadata, 'wb') as metadata_file:
        for row in trainLabels:
            row = np.argmax(row)
            metadata_file.write('%d\n' % row)
    with tf.Session() as sess:
        saver = tf.train.Saver([images])
        sess.run(images.initializer)
        saver.save(sess, os.path.join(LOG_DIR, 'images.ckpt'))
        config = projector.ProjectorConfig()
        embedding = config.embeddings.add()
        embedding.tensor_name = images.name
        embedding.metadata_path = metadata
        projector.visualize_embeddings(tf.summary.FileWriter(LOG_DIR), config)

def get_opt_atten_from_ind(mlData, atten_guess):
    # for i in range(12):
    #     print i, mlData.attens_orig[i], atten_guess[i]
    # print np.shape(mlData.attens_orig), np.shape(atten_guess)

    # print np.shape(mlData.attens_orig), np.shape(mlData.iq_vels_orig)
    mlData.opt_attens=np.zeros((len(atten_guess)))
    mlData.opt_freqs=np.zeros((len(atten_guess)))

    print np.shape(atten_guess), np.shape(mlData.good_res), 

    for r,a in enumerate(atten_guess):
        mlData.opt_attens[r] = mlData.attens_orig[r,a]
        mlData.opt_freqs[r] = mlData.freqs_orig[r, argmax(mlData.iq_vels_orig[r,a])]

    mlData.opt_attens = mlData.opt_attens[mlData.good_res]
    mlData.opt_freqs = mlData.opt_freqs[mlData.good_res]

    print np.shape(mlData.opt_attens), mlData.good_res
    # self.inferenceData.opt_attens[r] = self.inferenceData.attens[self.atten_guess[r]]
    # self.inferenceData.opt_freqs[r] = self.inferenceData.freqs[r,self.get_peak_idx(r,self.atten_guess[r])]
    return mlData

def reduce_PSFile(PSFile, good_res):
    print 'loading peak location data from %s' % PSFile
    PSFile = np.loadtxt(PSFile, skiprows=0)

    # opt_freqs = PSFile[:,1]
    # self.opt_attens = PSFile[:,2] #+ 1
    goodResIDs = PSFile[:,0]
    new_PSFile = np.zeros((len(good_res),3))
    for ir, r in enumerate(good_res):
        for c in range(3):
            new_PSFile[ir,c] = PSFile[np.where(goodResIDs == r)[0],c]

    return new_PSFile

def eval_vIQ_attens(mlData):
    ratio_guesses = np.zeros((len(mlData.good_res)))
    for r, _ in enumerate(mlData.good_res):
        _, _, ratio, _, _, _, _ = checkResAtten(mlData, res_num=r)

        # plt.plot(ratio)
        # print r, ratio,
        try:
            ratio_guesses[r] = np.where(ratio>3.5)[0][-1] + 2
        except IndexError:
            ratio_guesses[r] = np.argmin(ratio) + 2

        if ratio_guesses[r] >= len(ratio)-1:
            ratio_guesses[r] = len(ratio)- 2

        # print ratio_guesses[r]
        # plt.show()
    return ratio_guesses

def evaluateModel(mlClass, initialFile, showFrames=False, plot_missed=False, res_nums=50):
    '''
    The loopTrain() function evaluates true performance by running findAtten on the training dataset. The predictions 
    on the correct attenuation value for is resonator can then compared with what the human chose. Then you can see the 
    models accuracy and if their are any trends in the resonators it's missing
    '''
    print 'running model on test input data'

    mlClass.findPowers(inferenceFile=initialFile, searchAllRes=True, res_nums=res_nums)

    rawTrainData = mld.PSFitMLData(h5File = initialFile)
    rawTrainData.loadRawTrainData() # run again to get 

    # res remaining after manual flagging and cut to include up to res_nums
    # man_mask=rawTrainData.good_res[:np.where(rawTrainData.good_res<=res_nums)[0][-1]]
    man_mask=rawTrainData.good_res
    bad_man_mask = [] #res flagged by mlClass in man_mask 
    for item in mlClass.bad_res:
        try:
            bad_man_mask.append(list(man_mask).index(item) )
        except: pass
    rawTrainData.opt_iAttens =np.delete(rawTrainData.opt_iAttens, bad_man_mask)

    man_mask = np.delete(man_mask, bad_man_mask)

    atten_guess = mlClass.atten_guess[man_mask]
    # atten_guess_mode = mlClass.atten_guess_mode[man_mask]
    # atten_guess_mean = mlClass.atten_guess_mean[man_mask]
    # atten_guess_med = mlClass.atten_guess_med[man_mask]
    low_stds = mlClass.low_stds[man_mask]
    ratio_guess = mlClass.ratio_guesses[man_mask]

    correct_guesses = []
    bins = [5,3,1,0]

    def getMatch(bins=[5,3,1,0], metric=atten_guess, original=rawTrainData.opt_iAttens):
        matches = np.zeros((len(bins),len(atten_guess)))

        for ig, _ in enumerate(metric):
            for ib, b in enumerate(bins):
                if abs(metric[ig]-original[ig]) <=b: 
                    matches[ib,ig] = 1

        for ib, b in enumerate(bins):
            print 'within %s' % b, sum(matches[ib])/len(metric)

        return matches

    def plotCumAccuracy(matches, atten_guess, bins=[5,3,1,0]):
        cs = np.zeros((len(bins),len(atten_guess)))
        for ib,_ in enumerate(bins):
            cs[ib] = np.cumsum(matches[ib]/len(atten_guess))
        
        for ib, b in enumerate(bins):
            plt.plot(np.arange(len(atten_guess))/float(len(atten_guess))-cs[ib], label='within %i' % b)

        plt.legend(loc="upper left")
        plt.show()

    def getMissed(metric, original=rawTrainData.opt_iAttens):
        wrong_guesses=[]
        for ig, _ in enumerate(metric):            
            if abs(metric[ig]-original[ig]) >0:
                wrong_guesses.append(ig)

        return wrong_guesses

    # getMatch(bins, low_stds)
    # getMatch(bins, ratio_guess)
    matches = getMatch(bins, atten_guess)
    # matches = getMatch(bins, atten_guess_mean)
    # matches = getMatch(bins, atten_guess_med)

    wrong_guesses = getMissed(atten_guess,rawTrainData.opt_iAttens)

    # plotCumAccuracy(matches,atten_guess)

    def plotMissed(mlClass, man_mask, wrong_guesses, rawTrainData=None):
        for i, wg in enumerate(wrong_guesses):
            plotRes(mlClass, man_mask, wg, rawTrainData)

    # plotMissed(mlClass, man_mask, wrong_guesses, rawTrainData,)

    plot_confusion(rawTrainData.opt_iAttens, atten_guess, 'Manual Inspection', 'Neural Network')

    def plotBinComparison(rawTrainData, atten_guess):
        good_res = rawTrainData.good_res[:len(atten_guess)-1]
        # guesses_map = np.zeros((np.shape(rawTrainData.attens)[1],np.shape(rawTrainData.attens)[1]))
        good_mask = np.zeros((len(good_res)))
        print np.shape(good_res), np.shape(good_mask), 
        good_mask[good_res]=1
        print good_res, good_mask, np.shape(good_mask)
        # good_res = np.any(self.good_res == rn)
        #     one_hot[good_res] = 1
        guesses_map = np.zeros((2,2))

        for ia,ao in enumerate(good_mask):   
            ag = atten_guess[ia]
            guesses_map[ag,ao] += 1

        from matplotlib import cm
        import matplotlib.colors
        plt.imshow(guesses_map,interpolation='none', origin='lower', cmap=cm.coolwarm) #,norm = matplotlib.colors.LogNorm())
        plt.xlabel('actual')
        plt.ylabel('estimate')

        plt.colorbar(cmap=cm.afmhot)
        plt.show()

        plt.plot(np.sum(guesses_map, axis=0), label='actual')
        plt.plot(np.sum(guesses_map, axis=1), label='estimate')
        plt.legend(loc="upper left")
        plt.show()
    # plotBinComparison(rawTrainData, atten_guess)

    return matches
    
def plotRes(mlClass, man_mask, res=0, rawTrainData=None):
    # print res, man_mask[res], mlClass.atten_guess[man_mask[res]], '\t', rawTrainData.opt_iAttens[res], '\t', mlClass.low_stds[man_mask[res]] 
    fig, ax1 = plt.subplots()
    ax1.set_title(man_mask[res])
    ax1.plot(mlClass.inferenceLabels[man_mask[res],:], color='b',label='model')
    # ax1.plot(mlClass.max_2nd_vels[man_mask[res],:]/max(mlClass.max_2nd_vels[man_mask[res],:]),color='g', label='2nd vel')
    ax1.plot(mlClass.max_ratios[man_mask[res],:]/max(mlClass.max_ratios[man_mask[res]]),color='k', label='max vel')
    ax1.plot(mlClass.running_ratios[man_mask[res],:]/max(mlClass.running_ratios[man_mask[res],:]),color='g', label='running' )
    ax1.axvline(mlClass.atten_guess_mode[man_mask[res]], color='b', linestyle='--', label='machine')
    ax1.axvline(mlClass.ratio_guesses[man_mask[res]], color='g', linestyle='--', label='ratio')
    ax1.axvline(mlClass.low_stds[man_mask[res]], color='r', linestyle='--', label='angles')
    ax1.axvline(rawTrainData.opt_iAttens[res], color='k', linestyle='--', label='human')
    ax1.set_xlabel('Atten index')
    ax1.set_ylabel('Scores and 2nd vel')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    plt.legend()

    ax2 = ax1.twinx()
    ax2.plot(mlClass.ang_means[man_mask[res]], color='r', label='ang means')
    ax2.plot(mlClass.ang_stds[man_mask[res]], color='r', label='std means')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')

    plt.show()  

def get_common_good_res(mlData1, mlData2):
    print np.shape(mlData1.opt_iAttens), np.shape(mlData2.opt_iAttens)
    print mlData1.resIDs, mlData2.resIDs
    final_res = min([max(mlData1.resIDs), max(mlData2.resIDs)])
    print final_res

    print np.where(mlData1.resIDs >= final_res)[0][0], np.where(mlData2.resIDs >= final_res)[0][0]

    # from collections import Counter
    # print list((Counter(mlData1.resIDs) & Counter(mlData1.resIDs)).elements())

    good_res = []
    for r in range(int(final_res)):
        print r
        if r in mlData1.resIDs and r in mlData2.resIDs:
            print 'yep'
            good_res.append(r)

    print good_res, len(good_res)

    return good_res

def plot_agree_acc(**kwargs):#good_res, get_power_NN, var, opt_attens1):
    good_res = kwargs.pop('good_res')
    get_power_NN = kwargs.pop('get_power_NN')
    # var = kwargs.pop('var')
    opt_attens1 = kwargs.pop('opt_attens1')
    opt_attens2 = kwargs.pop('opt_attens2')
    h5File = kwargs.pop('h5File')
    
    mlClass = get_power_NN() 
    mlClass.findPowers(inferenceFile=h5File)
    
    # print mlClass.inferenceLabels[:,5], np.shape(mlClass.inferenceLabels)
    # mlClass.inferenceLabels = mlClass.inferenceLabels[good_res]


    mean = (opt_attens1 + opt_attens2)/2
    print mean[:10]
    var = np.sqrt(((opt_attens1-mean)**2 + (opt_attens2-mean)**2)/2)
    print var[:10]
    print argmax(var)
    def get_accuracies(opt_attens):


        # hist, bins = np.histogram(var)
        # plt.plot(hist, bins[:-1])
        # plt.show()
        def acc_from_int(inferenceLabel, opt_atten):
            '''accuracy from the integration method'''
            # print inferenceLabel, opt_atten
            accuracy = 0
            for ia, a in enumerate(inferenceLabel):
                # print ia,a, ia-opt_atten, len(inferenceLabel),
                accuracy += a*(1-abs(ia-opt_atten)/len(inferenceLabel))
                # print (1-abs(ia-opt_atten)/len(inferenceLabel)), accuracy
            return accuracy

        accuracies = np.zeros((len(good_res)))
        for ir, r in enumerate(good_res):
            # accuracies[ir] = mlClass.inferenceLabels[r,opt_attens[ir]]
            accuracies[ir] = acc_from_int(mlClass.inferenceLabels[r], opt_attens[ir])

        # print accuracies
        var_bins = np.unique(var)
        print var_bins
        sum_accuracies = np.zeros((len(var_bins)))
        amount_accuracies = np.zeros((len(var_bins)))
        acc_binned = [[] for i in range(len(var_bins))]
        print acc_binned, np.shape(acc_binned)

        for ia, a in enumerate(accuracies):
            for ivb, vb in enumerate(var_bins):
                if var[ia] == vb:            
                    sum_accuracies[ivb] += a
                    amount_accuracies[ivb] += 1
                    acc_binned[ivb].append(a)
        av_accuracies = sum_accuracies/amount_accuracies

        std_acc_bin = np.zeros((len(var_bins))) # standard deviation of all the accuracies for that manual inspection agreement bin 
        for ivb, vb in enumerate(var_bins):
            for iab,ab in enumerate(acc_binned[ivb]):
                std_acc_bin[ivb] += (ab - av_accuracies[ivb])**2
            std_acc_bin[ivb] = np.sqrt(std_acc_bin[ivb]/len(acc_binned[ivb]))

        print std_acc_bin, len(var_bins), amount_accuracies
        # plt.plot(var, accuracies, 'o')
        agg_bins = 1-var_bins/max(var_bins)

        return agg_bins, av_accuracies, amount_accuracies, std_acc_bin

    # plt.errorbar(var_bins, av_accuracies, yerr=std_acc_bin)
    # plt.scatter(var_bins, av_accuracies, s=amount_accuracies)
    SMALL_SIZE = 14
    MEDIUM_SIZE = 18
    BIGGER_SIZE = 22

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    #plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    plt.figure(figsize=(7, 6))

    # plt.scatter(agg_bins, av_accuracies, c='m', marker='s', s=10*amount_accuracies)
    cm = plt.cm.get_cmap('RdYlBu')

    agg_bins, av_accuracies, amount_accuracies, std_acc_bin = get_accuracies(opt_attens1)
    sing_ind = np.where(amount_accuracies==1)[0]
    doub_ind = np.where(amount_accuracies!=1)[0]
    sc = plt.scatter(agg_bins[doub_ind], av_accuracies[doub_ind], c=amount_accuracies[doub_ind], s=50, marker='s', cmap=cm)
    plt.errorbar(agg_bins, av_accuracies,c='m', yerr=std_acc_bin)
    plt.scatter(agg_bins[sing_ind], av_accuracies[sing_ind], c=amount_accuracies[sing_ind], s=50, marker='o', cmap=cm)

    _, av_accuracies, _, std_acc_bin = get_accuracies(opt_attens2)
    sc = plt.scatter(agg_bins[doub_ind], av_accuracies[doub_ind], c=amount_accuracies[doub_ind], s=50, marker='s', cmap=cm)
    plt.errorbar(agg_bins, av_accuracies,c='g', yerr=std_acc_bin)
    plt.scatter(agg_bins[sing_ind], av_accuracies[sing_ind], c=amount_accuracies[sing_ind], s=50, marker='o', cmap=cm)
    
    # plt.axhline(0.68,linestyle='--')
    # plt.axhline(0.88,linestyle='--')
    plt.xlabel('Manual Agreement')
    plt.xlim([-0.1, 1.1])
    plt.ylabel('Model Accuracy')
    plt.colorbar(sc)
    # plt.plot(var_bins, std_acc_bin)
    plt.show()

def compare_train_data(h5File, PSFile1, PSFile2, get_power_NN, plot_agree=True):
    mlData1 = mld.PSFitMLData(h5File = h5File, PSFile = PSFile1)
    mlData1.loadRawTrainData()

    mlData2 = mld.PSFitMLData(h5File = h5File, PSFile = PSFile2)
    mlData2.loadRawTrainData()
    
    good_res = get_common_good_res(mlData1, mlData2)
    # mlData1.resIDs = mlData1.resIDs[np.where(mlData1.resIDs == final_res)]

    opt_attens1 = np.zeros((len(good_res)))
    opt_attens2 = np.zeros((len(good_res)))
    
    for ir, r in enumerate(good_res):
        opt_attens1[ir] = mlData1.opt_iAttens[np.where(mlData1.resIDs == r)[0]]
        opt_attens2[ir] = mlData2.opt_iAttens[np.where(mlData2.resIDs == r)[0]]
    
    # mlData1.opt_iAttens = mlData1.opt_iAttens[:np.where(mlData1.resIDs >= final_res)[0][0]]
    # mlData2.opt_iAttens = mlData2.opt_iAttens[:np.where(mlData2.resIDs >= final_res)[0][0]]

    # mlData1.resIDs = mlData1.resIDs[:np.where(mlData1.resIDs >= final_res)[0][0]]
    # mlData2.resIDs = mlData1.resIDs[:np.where(mlData2.resIDs >= final_res)[0][0]]

    # print np.shape(mlData1.opt_iAttens), np.shape(mlData2.opt_iAttens)
    # print mlData1.resIDs, mlData2.resIDs

    kwargs = {'good_res': good_res,
    'get_power_NN' : get_power_NN,
    # 'var': var,
    'opt_attens1': opt_attens1,
    'opt_attens2': opt_attens2,
    'h5File': h5File}
    # 'PSFile1': PSFile1,
    # 'PSFile2': PSFile2}

    if plot_agree:
        plot_agree_acc(**kwargs)#, good_res, get_power_NN, var, opt_attens1, h5File, PSFile1, PSFile2)#plot_agree_acc()

    print opt_attens1, opt_attens2
    diff = abs(opt_attens1 - opt_attens2)
    print diff[:10]

    agreed_res=[]
    for ir, r in enumerate(good_res):
        if diff[ir]==0:
            agreed_res.append(r)

    print len(agreed_res)        
    return agreed_res, opt_attens1, opt_attens2

def plot_powers_hist(a_ipwrs, ml_ipwrs, mc_ipwrs):
    print 'probably want to do something like this: http://stackoverflow.com/questions/35308812/histtype-stepfilled-option-using-bar-function'
    print 'or this http://matplotlib.org/users/prev_whats_new/whats_new_1.5.html'

    # print a_ipwrs
    # from filled_step import filled_hist
    # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4.5), tight_layout=True)
    # hist, bins = np.histogram(ml_ipwrs, range(max_nClass+1))
    # filled_hist(ax1, bins, hist)
    # plt.show()
    # plt.figure(figsize=(8,8))
    # plt.fill_between(a_ipwrs, range(max_nClass), color="none", hatch="X", edgecolor="b", linewidth=0.0)
    # plt.hist(a_ipwrs, range(max_nClass + 1), facecolor='green', alpha=0.65, linewidth=0, label='analytical')
    # plt.hist(ml_ipwrs, range(max_nClass + 1), facecolor='blue', alpha=0.65, linewidth=0, label='neural network')
    # plt.hist(mc_ipwrs, range(max_nClass + 1), facecolor='red', alpha=0.65, linewidth=0, label='man inspection')
    # plt.legend()
    # plt.xlabel('Class label')

    # plt.figure(figsize=(8,8))
    # plt.hist((a_ipwrs, ml_ipwrs, mc_ipwrs), range(max_nClass + 1), alpha=0.65, color = ['green', 'blue', 'red'], label=('analytical', 'neural network', 'man inspection'))
    # plt.legend()
    # plt.xlabel('Class label')
    SMALL_SIZE = 14
    MEDIUM_SIZE = 18
    BIGGER_SIZE = 22

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    #plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    plt.figure(figsize=(8,8))

    hist, bins = np.histogram((ml_ipwrs+mc_ipwrs)/2 - a_ipwrs, range(max_nClass+1))
    plt.step(bins[:-1]+1, hist, 'g', linestyle='-',linewidth=2, label='analytical')
    plt.fill_between(bins[:-1], hist, color="none", hatch="/", edgecolor="g", linewidth=2, step='post')
    hist, bins = np.histogram((a_ipwrs+mc_ipwrs)/2 - ml_ipwrs, range(max_nClass+1))
    plt.step(bins[:-1]+1, hist, 'b', linestyle='--',linewidth=2, label='neural network')
    plt.fill_between(bins[:-1], hist, color="none", hatch='\\', edgecolor="b", linewidth=2, step='post')
    hist, bins = np.histogram((ml_ipwrs+a_ipwrs)/2 - mc_ipwrs, range(max_nClass+1))
    plt.step(bins[:-1]+1, hist, 'r', linestyle='-.',linewidth=2, label='man inspection')
    plt.fill_between(bins[:-1], hist, color="none", hatch="|", edgecolor="r", linewidth=2, step='post')
    plt.legend()
    plt.xlabel('Prediction Displacement')
    plt.show()
