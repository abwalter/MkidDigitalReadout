from matplotlib import rcParams, rc
import numpy as np
import sys
import scipy.interpolate
import scipy.signal
from baselineIIR import IirFilter
import matplotlib.pyplot as plt
import triggerPhotons as tP
import ipdb

def makeWienerNoiseSpectrum(data, peakIndices=[], numBefore=100, numAfter=700, noiseOffsetFromPeak=200, sampleRate=1e6, template=[],isVerbose=False,baselineSubtract=True):
    nFftPoints = numBefore + numAfter
    peakIndices=np.array(peakIndices).astype(int)
    
    #If no peaks, choose random indices to make spectrum 
    if len(peakIndices)==0:
        peakIndices=np.array([0])
        rate = len(data)/float(nFftPoints)/1000.
        while peakIndices[-1]<(len(data)-1):
            prob=np.random.rand()
            currentIndex=peakIndices[-1]
            peakIndices=np.append(peakIndices,currentIndex+np.ceil(-np.log(prob)/rate*sampleRate).astype(int))
        peakIndices=peakIndices[:-2]      
    if len(peakIndices)==0:
        raise ValueError('makeWienerNoiseSpectrum: input data set is too short for the number of FFT points specified')
    #Baseline subtract noise data
    if(baselineSubtract):
        noiseStream = np.array([])
        for iPeak,peakIndex in enumerate(peakIndices):
            if peakIndex > nFftPoints+noiseOffsetFromPeak and peakIndex < len(data)-numAfter:
                noiseStream = np.append(noiseStream, data[peakIndex-nFftPoints-noiseOffsetFromPeak:peakIndex-noiseOffsetFromPeak])
        data = data - np.mean(noiseStream)
    
    #Calculate noise spectra for the defined area before each pulse
    if len(peakIndices)>1000:
        noiseSpectra = np.zeros((len(peakIndices), nFftPoints))
    else:
        noiseSpectra = np.zeros((len(peakIndices), nFftPoints))
    rejectInd=np.array([])
    counter=0
    for iPeak,peakIndex in enumerate(peakIndices):
        if peakIndex > nFftPoints+noiseOffsetFromPeak and peakIndex < len(data)-numAfter:
            noiseData = data[peakIndex-nFftPoints-noiseOffsetFromPeak:peakIndex-noiseOffsetFromPeak]
            noiseSpectra[counter] = np.abs(np.fft.fft(data[peakIndex-nFftPoints-noiseOffsetFromPeak:peakIndex-noiseOffsetFromPeak])/nFftPoints)**2 
            counter+=1
            if len(template)!=0:
                filteredData=np.correlate(noiseData,template,mode='same')
                peakDict=tP.detectPulses(filteredData, nSigmaThreshold = 2., negDerivLenience = 1, bNegativePulses=True)
                if len(peakDict['peakIndices'])!=0:
                    rejectInd=np.append(rejectInd,counter-1)  
        if counter==500:
            break   
    noiseSpectra=noiseSpectra[0:counter]
    #Remove indicies with pulses by coorelating with a template if provided
    if len(template)!=0: 
        noiseSpectra = np.delete(noiseSpectra, rejectInd.astype(int), axis=0) 
    noiseFreqs = np.fft.fftfreq(nFftPoints,1./sampleRate)
    if len(np.shape(noiseSpectra))==0:
        raise ValueError('makeWienerNoiseSpectrum: not enough spectra to average')
    if np.shape(noiseSpectra)[0]<5:
        raise ValueError('makeWienerNoiseSpectrum: not enough spectra to average') 
           
    noiseSpectrum = np.median(noiseSpectra,axis=0)
    #noiseSpectrum[0] = 2.*noiseSpectrum[1] #look into this later 8/15/16
    if not np.all(noiseSpectrum>0):
        raise ValueError('makeWienerNoiseSpectrum: not all noise data >0')
    if isVerbose:
        print len(noiseSpectra[:,0]),'traces used to make noise spectrum', len(rejectInd), 'cut for pulse contamination'

    return {'noiseSpectrum':noiseSpectrum, 'noiseFreqs':noiseFreqs}
    
def covFromData(data,size=800,nTrials=None):
    nSamples = len(data)
    if nTrials is None:
        nTrials = nSamples//size
    data = data[0:nTrials*size]
    data = data.reshape((nTrials,size))
    data = data.T
    
    covMatrix = np.cov(data)
    covMatrixInv = np.linalg.inv(covMatrix)
    return {'covMatrix':covMatrix,'covMatrixInv':covMatrixInv}

def covFromPsd(powerSpectrum,size=None):
    autocovariance = np.abs(np.fft.ifft(powerSpectrum))
    if size is None:
        size = len(autocovariance)
    sampledAutocovariance = autocovariance[0:size]

    shiftingRow = np.concatenate((sampledAutocovariance[:0:-1],sampledAutocovariance))
    covMatrix = []

    for iRow in range(size):
        covMatrix.append(shiftingRow[size-iRow-1:size-iRow-1+size])

    covMatrix = np.array(covMatrix)

    covMatrixInv = np.linalg.inv(covMatrix)
    return {'covMatrix':covMatrix,'covMatrixInv':covMatrixInv,'autocovariance':sampledAutocovariance}
